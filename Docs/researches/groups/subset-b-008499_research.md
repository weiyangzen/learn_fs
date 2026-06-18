# subset-b-008499 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.cs -->
## sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.cs

Purpose: this C# file is the original Flow actor source-to-source compiler backend. It takes the parsed `Actor` tree produced by `ActorParser.cs`/`ParseTree.cs` and emits C++ classes that implement FoundationDB's legacy actor semantics on top of `Actor<T>`, `Future<T>`, callbacks, promises, cancellation, and generated state classes.

Important types and APIs: `Function` is an in-memory generated C++ function buffer with indentation, overload support, public/private generated-name handling, and `wasCalled` tracking. `Context` carries the active continuation function, next continuation, loop `break`/`continue` targets, active catch function, and loop-depth accounting. `StateVar` and `CallbackVar` describe generated state fields and callback base classes. `ActorCompiler.Write(TextWriter)` is the main entry point. It generates a state class, actor class, constructor/destructor/cancel method, callback functions, continuation functions, UID metadata, and the public wrapper function. Statement lowering is implemented by overloaded `CompileStatement` methods for `PlainOldCodeStatement`, `StateDeclarationStatement`, `ForStatement`, `RangeForStatement`, `WhileStatement`, `LoopStatement`, `ChooseStatement`, `BreakStatement`, `ContinueStatement`, `WaitStatement`, `CodeBlock`, `ReturnStatement`, `IfStatement`, `TryStatement`, and `ThrowStatement`.

Control flow: the compiler builds a continuation-passing control-flow graph. Synchronous code and loops without `wait` can be emitted as native C++; blocks that may suspend are split into generated `int` methods that pass and return `loopDepth`. `wait` is rewritten into a single-arm `choose`; `choose` creates callback base classes, callback fire/error functions, a shared exit function that removes outstanding callbacks, fast-ready branches, and callback registration on not-ready futures. Loops with waits are transformed into loop head/body/break/continue functions so that callback re-entry can resume at the right point and unwind nested loop levels. `try` creates catch continuation functions that only accept `Error`/`...`, and `throw` routes through the current generated catch function.

State and persistence behavior: actor parameters and `state` declarations become fields in the generated state class and survive suspension. Top-of-body state declarations are initialized in the state constructor; later state declarations are default-constructed and assigned at runtime. Range-for loops that suspend require the container to already be a state variable; the generated iterator is also persisted as state. Return paths explicitly destruct state, complete or error the actor promise, and delete/destroy the actor object. Callback groups are persisted via `actor_wait_state`, and cancellation switches on the current wait group to synthesize `actor_cancelled()` through callback error handling.

Dependencies and integration points: emitted C++ assumes Flow runtime classes and functions such as `Actor<T>`, `FastAllocated`, `ActorCallback`, `ActorSingleCallback`, `StrictFuture`, `FutureStream`, `ThreadFutureStream`, `SAV<T>`, `ActiveActorHelper`, `ActorIdentifier`, `ActorBlockIdentifier`, `ActorExecutionContextHelper`, `actorWaitStateIsWaiting`, `actorWaitStateIsCancelled`, `actor_cancelled`, and `unknown_error`. Optional probe generation calls `fdb_probe_actor_*`; ACAC instrumentation is generated under `WITH_ACAC`; sampling lineage is generated under `ENABLE_SAMPLING`. `uidObjects` records stable actor/block identifiers based on SHA-256 of source file and actor/function names for a `.uid` sidecar.

Risks: correctness depends on precise loop-depth arithmetic, callback cleanup, and state lifetime ordering. `ByteToLong` shifts after adding each byte, which preserves existing compiler behavior but is unusual and must remain compatible with UID expectations. The compiler uses reflection for statement dispatch, so new parse-tree statement types fail at runtime unless a matching private overload exists. It enforces several actor-language restrictions: only one catch clause, only `Error`/`...` catches, no unreachable code, no non-state range container across waits, and no missing value return for `Future<T>` actors. Code generation emits raw C++ strings, so parser normalization and line-number output are part of the correctness surface.

Test signals: expected validation is generated C++ compile success, actor semantic tests, cancellation/exception tests, line directive diagnostics, UID sidecar comparison, and parity with the Python actor compiler. The nearby benchmark files exercise coroutine/actor runtime performance, but this compiler itself is mainly tested indirectly by building `.actor.cpp` sources and comparing generated outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.xml -->
## sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.xml

Purpose: this Visual Studio/MSBuild rule schema declares the Flow Actor Compiler as a project item/tool. It lets `.actor.cpp` files be recognized by the IDE/build property system as `ActorCompiler` content.

Important types and APIs: the XML defines a `Rule` named `ActorCompiler` with `PageTemplate="tool"` and item type `ActorCompiler`. It exposes `EnableCompile` as a boolean option, `ActorCompilerOptions` as tool-specific options, and `AdditionalOptions` as command-line options passed onward to the C++ compiler handling generated output. It also maps `.actor.cpp` to the `ActorCompiler` content type and declares a separate `Dependency` item/content type.

Control flow: there is no executable control flow; MSBuild/Visual Studio loads this rule metadata to show property pages and bind file extensions to item types.

State and persistence behavior: properties persist in the project file through the `DataSource` configured with `Persistence="ProjectFile"` and `ItemType="ActorCompiler"`. The file itself does not store runtime state.

Dependencies and integration points: the schema uses `Microsoft.Build.Framework.XamlTypes`, `Microsoft.VisualStudio.Project.Contracts.Implementation`, and `mscorlib` XML namespaces. It integrates the C# actor compiler into Visual Studio project tooling rather than the Flow runtime.

Risks: build behavior can drift if property names no longer match project targets/tasks. The schema is IDE/build-system metadata, so errors may appear as missing property pages or incorrect `.actor.cpp` handling rather than compiler failures.

Test signals: validation is project load/build behavior in Visual Studio/MSBuild, correct recognition of `.actor.cpp`, and command-line construction that includes actor compiler and C++ additional options.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorCompiler.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorParser.cs -->
## sources/storage-engines/foundationdb/flow/actorcompiler/ActorParser.cs

Purpose: this C# file tokenizes mixed C++/Flow actor source, parses `ACTOR`, `SWIFT_ACTOR`, and `TEST_CASE` constructs into the parse tree, copies ordinary C++ through unchanged, and invokes `ActorCompiler` to replace actor bodies with generated C++.

Important types and APIs: `Error` carries source-line diagnostics. `ErrorMessagePolicy` controls warnings such as actors without waits and whether cancellable actors become `[[nodiscard]]` by default. `Token` records token text, absolute position, source line, brace depth, and parenthesis depth, and can compute matching token ranges. `TokenRange` provides range slicing/consuming and forward/reverse take/skip helpers. `BracketParser` and `AngleBracketParser` skip delimiters nested under square/angle brackets. `ActorParser.Write(TextWriter, string)` is the main source-to-source pass. Parsing routines include `ParseActorHeading`, `ParseTestCaseHeading`, `ParseCodeBlock`, `ParseStatement`, `ParseWaitStatement`, `ParseForStatement`, `ParseIfStatement`, `ParseTryStatement`, and class-context parsing for enclosing class names.

Control flow: construction tokenizes the whole file and computes nesting/source-line metadata. `Write` emits `#define POST_ACTOR_COMPILER 1`, preserves line directives, scans tokens, detects actor/testcase declarations, parses them, compiles each through `ActorCompiler`, injects generated C++, and resumes copying original tokens. It tracks brace depth and a class-context stack so actors inside classes can generate correct enclosing-class/friend information. Actor parsing distinguishes forward declarations by comparing the first semicolon against the first body brace.

State and persistence behavior: parser state is in-memory only: token arrays, source path, diagnostics policy, probe flag, and `uidObjects` propagated from compiled actors. No file persistence happens here; `Program.cs` owns output file writes. The output stream preserves original non-actor source and generated actor expansions with line-number mappings.

Dependencies and integration points: depends on `ActorCompiler` and parse-tree classes. It understands a restricted actor-language subset layered over C++: `state`, `wait`, `waitNext`, `choose`/`when`, `loop`, `try`/`catch`, `throw`, range/three-argument `for`, `if constexpr`, and `TEST_CASE`. It rejects unsupported constructs inside actors, including `goto`, `do`, `finally`, `__if_exists`, `__if_not_exists`, preprocessor directives, and `switch` blocks containing `return`.

Risks: the tokenizer is intentionally simple and token-preserving; complex modern C++ syntax can stress angle-bracket or declaration parsing. `ParseCodeBlock` finds statements by semicolon/brace at matching depth, so malformed or unsupported compound statements fail at parse time. Only uniform initialization for state variables is explicitly rejected; constructor/equal initialization are supported. `ParseWaitStatement` must correctly distinguish standalone waits, result declarations, state waits, and `waitNext`; mistakes here change generated callback signatures and state lifetime.

Test signals: generated actor output should compile and preserve diagnostics through `#line`. Parser-specific tests should cover nested classes/namespaces, actor forward declarations, template actors, attributes including `[[flow_allow_discard]]`, waits with local/state results, `choose` blocks with only `when`, `try`/`catch`, unsupported syntax errors, and no-wait warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ActorParser.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ParseTree.cs -->
## sources/storage-engines/foundationdb/flow/actorcompiler/ParseTree.cs

Purpose: this C# file defines the actor-language abstract syntax tree shared by the parser and compiler. It is intentionally lightweight: most C++ expressions remain normalized strings, while actor-specific control constructs become typed nodes.

Important types and APIs: `VarDeclaration` stores type, name, initializer text, and whether initialization used constructor syntax. `Statement` is the base with `FirstSourceLine` and virtual `containsWait()`. Concrete statements include plain C++ code, state declarations, while/for/range-for/loop, break/continue, if/constexpr-if, return, wait, choose/when, try/catch, throw, and `CodeBlock`. `Actor` stores attributes, return type, name, enclosing class, parameters, template formals, body, source line, static/uncancellable/testcase/namespace/forward-declaration flags, and helpers `IsCancellable()`/`SetUncancellable()`.

Control flow: there is no execution flow beyond recursive `containsWait()` methods. The compiler relies on those methods to decide whether it can emit native C++ control flow or must split into continuations.

State and persistence behavior: parse-tree objects are in-memory only. Semantically, `StateDeclarationStatement` and actor parameters represent data that `ActorCompiler` will persist in generated state classes; the parse tree itself does not perform persistence.

Dependencies and integration points: consumed by both `ActorParser.cs` and `ActorCompiler.cs`. It models only enough C++ syntax for the actor compiler, leaving expression and plain statement text opaque.

Risks: adding a statement node requires matching parser production, `containsWait()` behavior, and compiler lowering. Incorrect `containsWait()` can make the compiler emit native loops around suspending code or over-split non-suspending code. The file contains a BOM-like character before `using System`, so tooling should keep encoding stable.

Test signals: successful parser/compiler tests across every statement class, especially nested `containsWait()` cases, are the main validation. Static compilation will also catch missing `CompileStatement` overloads for newly introduced statement classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/ParseTree.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/Program.cs -->
## sources/storage-engines/foundationdb/flow/actorcompiler/Program.cs

Purpose: this C# file is the command-line entry point for the original actor compiler executable. It reads an input `.actor.cpp`, runs `ActorParser`, writes generated C++ to the requested output file, and writes a UID sidecar file.

Important APIs: `Main(string[] args)` parses `<input> <output> [--disable-diagnostics] [--generate-probes]`, configures `ErrorMessagePolicy`, constructs `ActorParser`, calls `parser.Write`, and serializes `parser.uidObjects` as `hi|lo|source-key` lines. `OverwriteByMove` replaces an output through a temporary file, normalizes the old target to writable before deletion, moves the temp file into place, then marks the result read-only.

Control flow: invalid arity prints usage and returns `100`. Actor-language errors return `1` with FAC1000 diagnostics and output cleanup. Unexpected exceptions return `3` with FAC2000 diagnostics and output cleanup. Success returns `0` after writing both generated output and `.uid`.

State and persistence behavior: file persistence is explicit and atomic-ish by temp-write plus move. Outputs are made read-only. On failures, the temporary and generated output are deleted; the code does not explicitly delete an already-written UID sidecar if the second phase fails after output replacement.

Dependencies and integration points: depends on the C# parser/compiler and `System.IO`. Build systems invoke this executable as a preprocessing step before compiling generated C++.

Risks: command-line parsing silently ignores unknown `--` options. `OverwriteByMove` deletes and moves instead of an atomic replace operation on all platforms, so interruption can leave no target file. The UID sidecar path is simply `<output>.uid`.

Test signals: CLI tests should verify exit codes, usage behavior, read-only output attributes, diagnostic toggles, probe generation flag forwarding, UID sidecar creation, and cleanup behavior after parser/compiler errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/Program.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/Properties/AssemblyInfo.cs -->
## sources/storage-engines/foundationdb/flow/actorcompiler/Properties/AssemblyInfo.cs

Purpose: this C# file supplies .NET assembly metadata for the actor compiler project.

Important APIs/types: assembly attributes define title/product as `actorcompiler`, description as `Compile Flow code to C++`, company as Apple Inc, COM visibility as false, typelib GUID, and assembly/file versions `1.0.0.0`.

Control flow: none; attributes are consumed by the compiler and runtime metadata readers.

State and persistence behavior: version and identity metadata are embedded in the compiled assembly. No runtime state is managed here.

Dependencies and integration points: uses `System.Reflection`, `System.Runtime.CompilerServices`, and `System.Runtime.InteropServices`. The metadata may affect packaging, file properties, and COM exposure.

Risks: copyright year and product metadata can drift from repository-wide conventions. Version numbers are fixed rather than generated, so package consumers cannot infer source revision from this file alone.

Test signals: build output inspection and assembly metadata checks are sufficient; functional actor compiler behavior is unaffected unless assembly metadata is used by packaging.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler/Properties/AssemblyInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/__main__.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/__main__.py

Purpose: this Python module is the module-mode CLI for the Python port of the Flow actor compiler, allowing invocation with `python3 -m flow.actorcompiler ...`.

Important APIs: `parse_arguments()` implements the same user-facing shape as the C# tool: required input/output plus `--disable-diagnostics` and `--generate-probes`; missing operands print usage and exit `100`. `overwrite_by_move()` makes an existing target writable, unlinks it, atomically replaces via `os.replace`, and marks the final file read-only. `main()` reads input, constructs `ActorParser`, writes generated output and `.uid`, and maps `ActorCompilerError` to FAC1000/exit `1` and unexpected exceptions to traceback plus FAC2000/exit `3`.

Control flow: parse args, announce command, compile to output temp, replace generated output, compile UID sidecar to the same temp path, replace UID, return success. Error paths remove temp and generated output if present.

State and persistence behavior: output files are rewritten from temporary files and then chmodded read-only for parity with the C# compiler. UID records are persisted as `hi|lo|source-key`. No persistent state exists beyond these files.

Dependencies and integration points: imports `ActorParser`, `ErrorMessagePolicy`, and `ActorCompilerError` from the Python actorcompiler package. Intended for build systems or comparison harnesses during migration from the C# compiler.

Risks: the code uses `Path.with_suffix(output_path.suffix + ".tmp")` and `.uid`, which gives paths like `file.g.cpp.tmp` and `file.g.cpp.uid`; this matches intent but differs from simple string append only for suffix-less paths. Broad exception handling prints a traceback, which is useful for migration but noisier than the C# FAC2000 path.

Test signals: CLI parity tests with the C# compiler, exit-code tests, FAC1000/FAC2000 diagnostics, chmod/read-only checks, and output/UID comparison are the primary validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/__main__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_compiler.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_compiler.py

Purpose: this Python file is a port of the C# actor compiler backend. It lowers the Python parse tree to generated C++ actor/state/callback/continuation code while preserving the semantics of Flow's original actor compiler.

Important types and APIs: `Function`, `LiteralBreak`, `LiteralContinue`, `StateVar`, `CallbackVar`, and `Context` mirror the C# helper model. `ActorCompiler.write(writer)` is the main generation entry point. Helper methods emit actor wrapper functions, actor classes, state constructors/destructors, generated functions, cancellation, templates, line directives, probes, ACAC instrumentation, and UID metadata. Statement dispatch uses `compile_statement()` to call methods named `_compile_<StatementClass>`, covering the same actor statements as the C# backend.

Control flow: the compiler constructs unique actor/state class names, handles forward declarations specially, seeds a body continuation and catch continuation, compiles the actor body into continuation functions, emits state/actor classes, then emits the public actor function and optional test-case macro. Suspension works through generated callbacks and `loopDepth` continuations. `wait` lowers to one-arm `choose`; `choose` creates fast-ready paths, callback registration, callback fire/error functions, and an exit function that clears wait state and removes callbacks. Loops containing waits are transformed into loop head/body/break/continue continuations; loops without waits use native C++.

State and persistence behavior: actor parameters and `state` declarations become generated state fields. Top-level state is constructor-initialized; later state is default-constructed and assigned. State wait results can be stored directly into generated state. Return paths explicitly destruct state and complete/delete actor runtime objects. Callback groups and wait state govern cancellation and callback removal.

Dependencies and integration points: depends on Python dataclasses from `parse_tree.py`, localized errors from `errors.py`, and Flow runtime symbols in generated C++. It also emits `WITH_ACAC`, `ENABLE_SAMPLING`, and optional `fdb_probe_actor_*` hooks. Its generated output is intended to be compared with C# output by `compare_actor_output.py`.

Risks: as a port, byte-for-byte or semantic drift from `ActorCompiler.cs` is the central risk. Notable surfaces include formatting of generated C++, UID byte conversion, overload output ordering, line-number directives, cancellation switch generation, and subtle loop-depth behavior. There are visible formatting differences in some string literals, such as the void actor `destroy()` branch using doubled braces in literal writes, that need output comparison coverage. Class-name uniqueness is reset by the parser before each file write.

Test signals: strongest tests are golden output comparisons against the C# actor compiler with normalized paths, generated C++ compilation, actor runtime behavior tests, cancellation/error propagation tests, and dedicated cases for `choose`, `waitNext`, state waits, range-for continuations, templates, nested classes, and no-wait diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_compiler.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_parser.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_parser.py

Purpose: this Python file is the parser/source-to-source front end for the Python actor compiler port. It tokenizes C++ actor source, parses actor-language constructs into Python dataclasses, and splices generated C++ from `actor_compiler.py` back into the output stream.

Important types and APIs: `ErrorMessagePolicy`, `Token`, `TokenRange`, `BracketParser`, `AngleBracketParser`, and `ActorParser` mirror the C# implementation. `ActorParser.write(writer, destFileName)` scans the source and expands `ACTOR`, `SWIFT_ACTOR`, and `TEST_CASE`. Parsing helpers include `parse_actorHeading`, `parse_test_caseHeading`, `parse_declaration`, `parse_var_declaration`, `parse_wait_statement`, `parse_for_statement`, `parse_code_block`, `parse_statement`, and `parse_class_context`.

Control flow: initialization tokenizes via ordered regular expressions and annotates brace/paren depth and source lines. `write` clears class-name global state, writes `POST_ACTOR_COMPILER`, tracks output line numbers and class nesting, invokes `ActorCompiler` for actor constructs, merges UID objects, and otherwise copies tokens through. Parsing distinguishes forward declarations from definitions, fills actor namespace/enclosing-class data, warns on no-wait actors, and rejects unsupported actor-local syntax.

State and persistence behavior: parser state is in memory: token list, source path, line-number flag, error policy, probe flag, UID map, and a private `_parse_end` cursor. It does not write files directly; `__main__.py` owns persistence.

Dependencies and integration points: imports `ActorCompiler`, parse-tree dataclasses, and `ActorCompilerError`. It must remain grammar-compatible with C# actor source accepted by the original compiler, including templates, attributes, `UNCANCELLABLE`, `[[flow_allow_discard]]`, `[[nodiscard]]` insertion, `state`, `wait`, `waitNext`, `choose`/`when`, loops, `try`/`catch`, and tests.

Risks: migration drift is the major risk. Differences from C# naming/casing are internal, but output behavior must match. The parser uses regex tokenization and simple declaration splitting; complex C++ types, nested templates, attributes, and initializers are sensitive. `parse_wait_statement` sets `is_wait_next` by scanning initializer tokens after accepting either wait keyword; this is clear but should be covered. `parse_compound_statement` assumes non-braced single statements can be parsed from `toks.skip(1)`, matching C# behavior but easy to break if token range semantics change.

Test signals: compare generated outputs against the C# compiler, especially for line directives, attributes, namespace/class nesting, template actors, forward declarations, `TEST_CASE`, state declarations, waits, `waitNext`, `choose`, illegal keyword errors, and no-wait warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/actor_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/compare_actor_output.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/compare_actor_output.py

Purpose: this utility compares two generated actor compiler outputs, allowing path differences inside `#line` directives so C# and Python compiler outputs can be checked for semantic/textual parity.

Important APIs: `compare_outputs(file1_path, file2_path)` reads both files, returns true for exact equality, normalizes quoted filenames in `#line <number> "path"` directives to `NORMALIZED_PATH`, compares again, and prints a unified diff of normalized content on mismatch. `main()` parses two path arguments and exits nonzero if comparison fails.

Control flow: exact compare first, normalized compare second, diff/false on mismatch, exception/false on read or comparison errors.

State and persistence behavior: read-only utility; it writes only diagnostics to stderr.

Dependencies and integration points: uses `argparse`, `pathlib`, `re`, `difflib`, and `sys`. It is a migration/test helper for proving the Python actor compiler matches the existing generated output apart from source path differences.

Risks: normalization is intentionally narrow; differences in line numbers, whitespace, generated identifiers, or UID output still fail. It compares one file pair and does not handle UID sidecars unless explicitly passed as inputs. The regex only normalizes `#line` directives with quoted paths.

Test signals: unit tests should cover exact match, path-only line-directive differences, real content differences with diff output, missing files, and generated actor outputs from both compilers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/compare_actor_output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/errors.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/errors.py

Purpose: this tiny Python module defines the location-aware exception type shared by the Python parser and compiler.

Important APIs: `ActorCompilerError(source_line, message, *args)` formats optional arguments with `str.format`, stores `source_line`, and renders as `<message> (line <source_line>)`.

Control flow: no complex flow; exceptions are raised by parser/compiler code and caught by the CLI.

State and persistence behavior: exception objects carry source-line state only in memory. No persistence.

Dependencies and integration points: imported by `actor_parser.py`, `actor_compiler.py`, and `__main__.py`. The CLI maps it to FAC1000 diagnostics.

Risks: because messages are formatted with Python `str.format`, literal braces in messages must be escaped. Source line `0` is used for some internal errors and may produce less useful user diagnostics.

Test signals: tests should verify message formatting, string rendering, source-line retention, and CLI FAC1000 output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/errors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/parse_tree.py -->
## sources/storage-engines/foundationdb/flow/actorcompiler_py/parse_tree.py

Purpose: this Python file defines the dataclass AST used by the Python actor compiler port. It mirrors `ParseTree.cs` while using Python naming and type annotations.

Important types and APIs: `VarDeclaration`, abstract `Statement`, `CodeBlock`, `PlainOldCodeStatement`, `StateDeclarationStatement`, `WhileStatement`, `ForStatement`, `RangeForStatement`, `LoopStatement`, `BreakStatement`, `ContinueStatement`, `IfStatement`, `ReturnStatement`, `WaitStatement`, `ChooseStatement`, `WhenStatement`, `TryStatement` with nested `Catch`, `ThrowStatement`, and `Actor`. Each statement implements `contains_wait()`; `Actor` implements `is_cancellable()` and `set_uncancellable()`.

Control flow: no runtime actor control flow is executed. Recursive `contains_wait()` is the key behavioral API used by `actor_compiler.py` to choose native C++ emission or continuation splitting.

State and persistence behavior: dataclasses are transient parse results. Actor parameters and state declarations are later converted into generated C++ state fields, but this file does not persist anything itself.

Dependencies and integration points: depends on `abc`, `dataclasses`, and typing primitives. Consumed by `actor_parser.py` and `actor_compiler.py`.

Risks: default factories avoid shared mutable defaults for statement bodies and lists. Any new statement class must implement `contains_wait()` and be added to parser/compiler dispatch. Because `Statement.contains_wait` is abstract, accidental instantiation of base statements is prevented.

Test signals: parser/compiler tests indirectly validate all dataclasses. Direct unit tests can verify `contains_wait()` propagation through nested blocks, if/else, loops, choose/when, and try/catch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/actorcompiler_py/parse_tree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchAsyncResult.cpp -->
## sources/storage-engines/foundationdb/flow/bench/BenchAsyncResult.cpp

Purpose: this benchmark file measures C++20 coroutine performance for `Future<T>` versus `AsyncResult<T>` and aggregation helpers when moving/copying moderately expensive payloads through Flow async APIs.

Important types and APIs: `ExpensivePayload` owns a byte vector initialized with `std::iota` and a `touch()` method that reads first/middle/last bytes. `returnFuturePayload` and `returnAsyncResultPayload` are coroutine producers. Benchmark template families cover single await (`benchAwaitPayloadActor`/`benchAwaitPayload`), `getAll`/`getAllAsync` over `Future<ExpensivePayload>` inputs, and `getAll`/`getAllAsync` over freshly produced `AsyncResult<ExpensivePayload>` inputs. Enum template parameters select implementation variants.

Control flow: each benchmark runs a Flow coroutine on the main thread via `onMainThread(...).blockUntilReady()`. Inside `benchmark::State` loops, it awaits or aggregates payload futures/results, touches payloads to prevent dead-code elimination, calls `ClobberMemory`, and records processed bytes.

State and persistence behavior: state is benchmark-local. Payload sources are reused where appropriate; some variants allocate vectors of async results inside each iteration to include production/aggregation cost. No persistent storage is touched.

Dependencies and integration points: depends on Google Benchmark, Flow coroutine/future APIs from `flow/flow.h`, `flow/genericactors.actor.h`, and `flow/ThreadHelper.actor.h`. It benchmarks runtime coroutine paths rather than actor compiler output.

Risks: benchmark numbers depend on payload copy elision/move behavior, vector allocation, main-thread scheduling overhead, and whether inputs are already ready. The `AsyncResult` aggregate benchmark constructs inputs inside the timing loop, so it measures more than aggregation alone. `ASSERT(!bytes.empty())` assumes benchmark ranges are nonzero.

Test signals: build success with coroutine-enabled Flow, benchmark registration names, nonzero bytes processed, and stable relative results across payload sizes. It can also catch regressions in `getAll`/`getAllAsync` support for `AsyncResult`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchAsyncResult.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCallback.cpp -->
## sources/storage-engines/foundationdb/flow/bench/BenchCallback.cpp

Purpose: this benchmark file measures callback fan-out/fan-in overhead using C++20 coroutine-style Flow code. The comment positions it as a coroutine version of callback benchmarks matching a `BenchNet2.cpp` pattern.

Important APIs: `incrementCoro<Size>(Future<Void>, uint32_t*)` allocates a stack buffer of `Size`, waits on a trigger future, prevents optimization of the buffer, and increments a shared sum. `benchCallbackCoro<Size>` creates many increment coroutines waiting on one promise, sends the trigger, waits for all futures, and records processed items/bytes. `coroutine_callback<Size>` runs the benchmark actor on the main thread.

Control flow: for each benchmark iteration, create `actorCount` futures, trigger them all with one `Promise<Void>`, await `waitForAll`, and account for work. Template registrations cover stack sizes 1, 32, and 1024 with actor counts from 1 to 256.

State and persistence behavior: benchmark state is local: `sum`, `Promise`, and vector of futures per iteration. No persistence.

Dependencies and integration points: depends on Google Benchmark and Flow headers (`IRandom`, `flow`, `DeterministicRandom`, `network`, `ThreadHelper.actor.h`), though random/network includes are not directly used in the visible code. It integrates with Flow's main-thread execution helper.

Risks: `uint8_t arr[Size]` is uninitialized but only passed to `DoNotOptimize`; this is acceptable for benchmarking stack footprint but compiler behavior should be watched. The shared `sum` pointer assumes all continuations run cooperatively on the Flow main thread, avoiding data races. Include drift can add unnecessary compile dependencies.

Test signals: benchmark compile/register/run, items and bytes processed matching actor count and size, and comparison against actor-style callback benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCallback.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCallbackActor.cpp -->
## sources/storage-engines/foundationdb/flow/bench/BenchCallbackActor.cpp

Purpose: this benchmark file measures the same callback fan-out/fan-in shape as `BenchCallback.cpp`, using Flow coroutine functions named in the actor benchmark style.

Important APIs: `increment<Size>(Future<Void>, uint32_t*)` allocates a `std::array<uint8_t, Size>`, awaits a trigger future, prevents optimization, and increments a shared sum. `benchCallbackActor<Size>` creates `actorCount` increments, sends the trigger, awaits `waitForAll`, and records item/byte throughput. `bench_callback<Size>` runs it on the main thread. Benchmark registrations cover sizes 1, 32, and 1024 over range 1 to 256.

Control flow: per iteration, reset `sum`, create one promise and many futures, fire the promise, wait for all callbacks to resume, and update benchmark counters after the loop.

State and persistence behavior: all state is local to the benchmark and coroutine frames. No persistent storage.

Dependencies and integration points: depends on Google Benchmark, `flow/flow.h`, and `flow/ThreadHelper.actor.h`. It is a performance integration point for Flow future/coroutine scheduling and callback fan-out.

Risks: the function returns `Future<Void>` but falls off the end without an explicit `co_return`; this may compile due to coroutine promise behavior but is a portability/readability risk compared with the explicit `co_return` in `BenchCallback.cpp`. As with the coroutine variant, shared `sum` assumes single-threaded cooperative execution. `std::array` requires the included headers to supply `<array>` transitively or elsewhere.

Test signals: successful compilation, benchmark registration, processed counters, and comparison against `BenchCallback.cpp` and historical actor callback benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCallbackActor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchConflictSet.cpp -->
## sources/storage-engines/foundationdb/flow/bench/BenchConflictSet.cpp

Purpose: this benchmark compares a simple `std::vector<bool>` conflict set against a word-packed `uint64_t` bitset implementation for FoundationDB-style range conflict detection workloads.

Important types and APIs: `MiniConflictSet` stores one boolean per key and implements `set(begin,end)`, `any(begin,end)`, and `clear()`. `WordBitsetConflictSet` stores 64-bit words and implements the same API with range masks across partial and full words. `ConflictRange` holds begin/end. `getSharedWorkload` creates deterministic static write/query ranges parameterized by number of ranges, keyspace, sparsity, and workload type. Benchmarks cover set/query for both implementations, a correctness verification benchmark, and a realistic combined write/read workload selected by template parameter.

Control flow: workload generation seeds deterministic random state and builds static vectors once per template instantiation. Set benchmarks construct a fresh conflict set each iteration and apply ranges. Query benchmarks prepopulate once, then count conflicts over read ranges inside the timed loop. Realistic benchmarks perform both writes and reads per iteration. Correctness benchmark compares both implementations over shared workloads and calls `SkipWithError` on mismatch.

State and persistence behavior: all state is in-memory benchmark data. Static workload vectors persist for the process lifetime to avoid regeneration inside timed loops. No external persistence.

Dependencies and integration points: depends on Google Benchmark, Flow `IRandom`, `Error`/`ASSERT`, standard vectors/algorithms/cstdint/limits. The benchmark models behavior similar to a conflict set from `SkipList.cpp` and can inform replacement or optimization decisions.

Risks: neither implementation does bounds checks on `begin`/`end` beyond empty ranges; workload generation must keep ranges within keyspace. `WordBitsetConflictSet` must avoid undefined shifts; it handles single-word `numBits == 64`, and multi-word masks use `(end - 1) % 64`, but edge cases around zero-size keyspaces or invalid ranges would be dangerous. `std::vector<bool>` has proxy semantics, so benchmarking it against word operations is useful but not a drop-in production proof. Static deterministic workloads are reproducible but may underrepresent real transaction distributions.

Test signals: `CorrectnessTest/VerifyAllImplementations` is the main safety signal. Additional useful tests include boundary ranges crossing word boundaries, single-bit and full-word ranges, empty ranges, dense workloads, and realistic workload benchmark stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchConflictSet.cpp -->
