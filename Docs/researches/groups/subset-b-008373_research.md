# subset-b-008373 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/yacc.py -->
# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/yacc.py

## Purpose
This file is the vendored PLY yacc implementation used by sepolgen's reference-policy parser. It turns grammar functions with BNF docstrings into SLR or LALR(1) parse tables, persists those tables as Python modules or pickles, and exposes an `LRParser` runtime that consumes tokens from the companion lexer. It is infrastructure code rather than SELinux-domain logic, but correctness here controls every parser built on top of `sepolgen.refparser`.

## Important APIs, Types, And Functions
The public construction entry point is `yacc(...)`, with options for parser method, debug output, module/tabmodule selection, start symbol, recursion checks, table writing, output directory, loggers, and pickle files. It uses `ParserReflect` to inspect a grammar module for `tokens`, `precedence`, `start`, `p_error`, and `p_*` production functions.

`LRParser` is the runtime parser. `parse()` dispatches to `parsedebug`, `parseopt`, or `parseopt_notrack` depending on debug and tracking flags. `restart()`, `errok()`, `disable_defaulted_states()`, and the `token` method support parser state control and panic-mode error recovery.

`YaccSymbol` represents parser stack symbols, and `YaccProduction` is the list-like object passed into grammar actions. It exposes values by index, location helpers (`lineno`, `linespan`, `lexpos`, `lexspan`), parser/lexer references, and `error()` which raises `SyntaxError` to trigger recovery.

`Grammar`, `Production`, `MiniProduction`, and `LRItem` model grammar metadata and LR item state. `Grammar` validates productions, precedence, start symbols, undefined symbols, unreachable symbols, unused terminals/rules, infinite recursion, FIRST sets, FOLLOW sets, and LR items.

`LRTable` reads generated table modules or pickle files, validates `__tabversion__`, and binds production names back to callables. `LRGeneratedTable` builds LR(0), SLR, and LALR table data, resolves conflicts with precedence/associativity, records conflict diagnostics, and writes or pickles parse tables.

## Control Flow
`yacc()` obtains a parser namespace from the supplied module or caller stack, resolves the output directory, applies package-qualified tabmodule handling, reflects and validates grammar metadata, computes a grammar signature, and tries to load existing tables. If an optimized or signature-matching table loads, callables are rebound and an `LRParser` is returned.

If no table is reusable, `yacc()` validates parser functions, builds a `Grammar`, registers precedence and productions, checks undefined symbols, unused symbols, unreachable symbols, infinite recursion, and unused precedence, then creates an `LRGeneratedTable`. The generated table is optionally written to a tabmodule or pickle before an `LRParser` is returned.

At parse time, `LRParser` keeps explicit state and symbol stacks. It gets lookahead tokens from either `lexer.token()` or a supplied `tokenfunc`, shifts positive actions, reduces negative actions by invoking the grammar callable with a `YaccProduction`, and returns on action `0`. Syntax errors create or propagate an `error` symbol, call `p_error` once per recovery window, and discard input or pop parser state according to yacc-style panic recovery.

Table generation starts with LR(0) closure and goto sets, then optionally computes LALR lookaheads using nullable nonterminals, nonterminal transitions, DR/READS relations, lookback/includes relations, and the `digraph()` propagation helper. `lr_parse_table()` walks each item set to build action/goto rows and applies conflict resolution.

## State And Persistence
Parser runtime state lives in `statestack`, `symstack`, `lookahead`, `lookaheadstack`, `errorok`, `state`, and defaulted-state maps. Deprecated module globals `_errok`, `_token`, and `_restart` are temporarily rebound while calling old-style `p_error` implementations.

Generated parser state persists as a Python tabmodule containing `_tabversion`, `_lr_method`, `_lr_signature`, `_lr_action`, `_lr_goto`, and `_lr_productions`, or as a pickle with equivalent data. Debug mode writes `parser.out` by default. The module-level global `parse` is rebound to the last built parser's `parse` method, which is a legacy convenience but also global mutable state.

## Dependencies And Integration Points
The file depends only on the Python standard library (`re`, `types`, `sys`, `os.path`, `inspect`, `warnings`, and pickle modules) plus relative import `.lex` at parse time when no lexer is supplied. It is integrated by grammar modules that define `tokens`, optional `precedence`, optional `start`, optional `p_error`, and production functions named `p_*` with grammar docstrings.

The sepolgen tests in this subset indirectly exercise this file through `sepolgen.refparser.parse(...)`, especially interface parsing and interface expansion tests. Table files (`parsetab.py`) and debug output (`parser.out`) are explicitly cleaned by the sepolgen test Makefile.

## Risks And Edge Cases
The code intentionally duplicates parser logic between debug, optimized tracking, and optimized no-tracking paths, so fixes to parser behavior can diverge if not mirrored. Global `parse` and deprecated error-recovery globals are not thread-safe. Table import uses dynamic `exec('import %s' % module)` and therefore depends on trusted module names and Python import path state.

`Grammar.add_production()` uses `eval()` for quoted literal token syntax; that is normal PLY behavior but should remain limited to trusted grammar source. Table loading with `optimize=True` accepts tables without requiring a signature match, which can mask stale grammar/table mismatches. Conflict resolution defaults to shifting unless precedence requires otherwise, so grammar changes can silently alter parse choices while only producing warnings.

## Test Signals
There is no direct unit test for `yacc.py` in this subset. `test_refparser.py`, `test_interfaces.py`, and `test_matching.py` all depend on successful yacc/lexer integration for parsing reference policy interface snippets. The test Makefile removes generated `parser.out` and `parsetab.py`, indicating parser table generation is expected during tests or development runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/sepolgen/yacc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/share/Makefile -->
# sources/security-integrity/selinux/python/sepolgen/src/share/Makefile

## Purpose
This Makefile installs sepolgen shared data, specifically `perm_map`, into the configured data directory. The data is consumed by the object model permission mapping tests and by sepolgen runtime components that need permission direction and weight metadata.

## Important Targets And Variables
`SHAREDIR ?= /var/lib/sepolgen` controls the install location. `all` is a no-op placeholder. `install` creates `$(DESTDIR)$(SHAREDIR)` and installs `perm_map` with mode `644`. `clean` removes editor backup files matching `*~`.

## Control Flow
The install path is standard make flow: `install` depends on `all`, ensures the destination directory exists, then copies `perm_map`. There is no build-time generation.

## State And Persistence
The only persistent artifact is the installed `perm_map` file under the share directory. `DESTDIR` supports packaging roots without changing the final logical `SHAREDIR`.

## Dependencies And Integration Points
It depends on shell tools `mkdir` and `install`, and on the source-side `perm_map` file. `tests/test_objectmodel.py` opens `perm_map` locally during tests, while installed consumers normally expect `/var/lib/sepolgen/perm_map`.

## Risks And Edge Cases
The `-mkdir` prefix ignores directory creation failures, which may hide install problems until `install` fails. The Makefile does not install any other share data and assumes `perm_map` exists in the current working directory. There is no uninstall target.

## Test Signals
No direct Makefile test exists. The object-model test validates the semantics of a readable `perm_map` fixture by checking `filesystem mount` and default permission behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/src/share/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/Makefile -->
# sources/security-integrity/selinux/python/sepolgen/tests/Makefile

## Purpose
This Makefile is the local test harness for sepolgen's Python unit tests. It centralizes cleanup of generated parser, bytecode, module-compile, and test-output artifacts, and invokes the aggregated `run-tests.py` runner.

## Important Targets And Variables
`PYTHON ?= python3` controls the interpreter. `test` runs `$(PYTHON) run-tests.py`. `clean` removes backups, bytecode, yacc table/debug files (`parser.out`, `parsetab.py`), module compiler outputs (`module_compile_test.fc`, `.if`, `.pp`), generic `output`, `__pycache__`, and `tmp`.

## Control Flow
The only executable workflow is `make test`, which delegates all discovery/import ordering to `run-tests.py`. `make clean` is manual hygiene around tests with file-system side effects.

## State And Persistence
The Makefile does not persist state itself, but it acknowledges several tests create local files. `test_interfaces.py` writes `output`, parser generation may write `parser.out` and `parsetab.py`, and `test_module.py` creates compiled SELinux module artifacts.

## Dependencies And Integration Points
It depends on the Python unit test suite in the same directory and any external SELinux toolchain needed by those tests. It is tightly coupled to exact generated filenames; if module compiler output names change, cleanup will become stale.

## Risks And Edge Cases
The cleanup target uses broad globs such as `*~` and `*.pyc` but is scoped to the test directory. The test target does not set environment variables, so it relies on `run-tests.py` to adjust `sys.path` and on the caller's working directory for fixtures like `audit.txt`, `perm_map`, and `module_compile_test.te`.

## Test Signals
The presence of cleanup for parser and module artifacts signals expected side effects from parser generation and external SELinux module compilation. Successful `make test` should leave only ignored or cleanup-removable outputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/run-tests.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/run-tests.py

## Purpose
This is the aggregate unittest runner for sepolgen. It makes the local source tree importable and imports every test module so `unittest.main()` can discover their `TestCase` classes.

## Important APIs And Flow
The runner inserts `../src/.` at the front of `sys.path`, then imports all tests with wildcard imports: access, audit, refpolicy, refparser, policygen, matching, interfaces, objectmodel, and module. When invoked as a script it calls `unittest.main()`.

## State And Persistence
It mutates process import state by prepending the local sepolgen source directory to `sys.path`. It does not write files directly, but imported tests do.

## Dependencies And Integration Points
It depends on the test files being importable from the current directory and on sepolgen modules being available under `../src/.`. The import order matters only insofar as wildcard imports can overwrite globals; unittest discovery finds classes regardless.

## Risks And Edge Cases
Wildcard imports make namespace collisions possible and obscure which module defines a test name. The script assumes it is run from the tests directory; from another working directory, `../src/.` and local fixture files may not resolve correctly. It uses legacy unittest aggregation rather than explicit discovery.

## Test Signals
It is the authoritative entry point for the tests in this subset and is invoked by the tests Makefile. A passing run exercises parser, policy model, access vector, audit parsing, interface, object model, policy generation, matching, and module compiler behaviors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/run-tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_access.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_access.py

## Purpose
This unit test file validates sepolgen access-vector data structures and conversions between reference-policy rules and normalized access vectors. It is focused on object construction, list/string serialization, comparisons, extended permissions, and grouped `AccessVectorSet` behavior.

## Important Tests And Exercised APIs
`TestAccessVector` covers `AccessVector` default state, `from_list`, `to_list`, `to_string`/`__str__`, ordering/equality, plain permission merge, and extended permission merge by operation. It uses `refpolicy.IdSet` and `refpolicy.XpermSet`.

`TestUtilFunctions` covers `is_idparam()` and `avrule_to_access_vectors()`, confirming cartesian expansion across source types, target types, object classes, and permissions from a `refpolicy.AVRule`.

`TestAccessVectorSet` covers creation, iteration, length, list round-trips, adding first and subsequent vectors, merging permissions under the same source/target/class/type key, storing audit messages, and the convenience `add()` wrapper.

## Control Flow
The tests construct policy objects directly, mutate their public attributes, then assert normalized data. `setUp()` builds an `AVRule`, converts it to eight access vectors, and inserts them into an `AccessVectorSet` used by multiple tests.

## State And Persistence
All state is in-memory except the shared `self.s` fixture per test case. `AccessVectorSet` internal state is validated through iteration, length, and `to_list()`, plus direct access to `src['foo']['bar']['file', av.type].audit_msgs`.

## Dependencies And Integration Points
The file imports `sepolgen.refpolicy`, `sepolgen.refparser`, `sepolgen.policygen`, and `sepolgen.access`; only `refpolicy` and `access` are materially used in the tests. It checks the contract that policy generators and audit parsers depend on: normalized access vectors must merge and compare predictably.

## Risks And Edge Cases
Two methods named `text_merge_xperm1` and `text_merge_xperm2` appear intended as tests but do not start with `test_`, so unittest will not execute them. Their assertions also expect merged plain permissions that are not present in the constructed inputs, suggesting they may be stale. Ordering assertions against set-like structures are partly normalized with sorting, but some direct `list(...)` assertions still rely on deterministic behavior from local types.

## Test Signals
This file is a strong signal for access-vector serialization, xperm merge semantics, and `AccessVectorSet` deduplication. It does not exercise parsing from actual policy text, despite importing parser modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_access.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_audit.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_audit.py

## Purpose
This file tests audit log parsing and conversion of AVC records into access vectors. It uses embedded syslog/auditd AVC samples, AVC_PATH records, granted records, and ioctl extended-permission records.

## Important Tests And Exercised APIs
`TestAVCMessage` validates `AVCMessage` default fields, parsing of granted and denied records, SELinux source/target context fields, target class, access list, command name, denial flag, and `ioctlcmd` parsing including invalid or missing values.

`TestPathMessage` validates `AVC_PATH` extraction. `TestAuditParser` validates `parse_string()`, `parse_file()`, path post-processing across records with matching audit IDs, and xperm aggregation in `to_access()`. `TestGeneration` checks that denied records produce access vectors by default and granted records require `only_denials=False`.

## Control Flow
Tests instantiate parser/message classes, split embedded log strings, call `from_split_string()` or parser methods, and assert parsed fields. `parse_file()` opens a local `audit.txt` fixture from the current working directory. Xperm tests parse multiple AVCs with the same source/target/class and verify ioctl command ranges are coalesced into an `XpermSet`.

## State And Persistence
Most state lives inside message objects and `AuditParser` collections: `avc_msgs`, `compute_sid_msgs`, `invalid_msgs`, `policy_load_msgs`, and `path_msgs`. The file reads but does not write `audit.txt`.

## Dependencies And Integration Points
It depends on `sepolgen.audit` and `sepolgen.refpolicy`. Its output path integrates with `sepolgen.access.AccessVectorSet`, which is later used by policy generation. The test data covers both syslog-prefixed and audit daemon formats.

## Risks And Edge Cases
The parser is tested with a narrow set of historical log formats; TODO comments explicitly call for more message types and more log examples. Tests assume local fixture files and do not isolate the working directory. Invalid ioctl parsing is expected to silently yield `None`, so failures may be non-fatal by design.

## Test Signals
The file provides meaningful regression signals for AVC context parsing, granted/denied filtering, AVC_PATH correlation, and ioctl xperm range generation. It does not directly verify malformed record recovery beyond invalid ioctl values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_audit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_interfaces.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_interfaces.py

## Purpose
This test file validates extraction and expansion of SELinux reference-policy interfaces into access-vector summaries. It checks parameter typing, interface parsing, nested interface-call expansion, and export/import of interface metadata.

## Important Tests And Exercised APIs
`TestParam` validates `interfaces.Param`, including `$N` validation, numeric extraction, and default source-type classification. `TestAVExtractPerms` exercises `av_extract_params()` across source parameters, target parameters, process class special cases, and directory target behavior.

`compare_avsets()` builds an `AccessVectorSet` from a list and compares it to another set after sorting. `TestInterfaceSet.test_simple()` parses a simple interface, adds headers into `InterfaceSet`, and checks interface name, access vectors, and required parameter metadata. `test_expansion()` validates nested interface expansion across `foo`, `map`, and `hard_map`. `test_export()` writes `InterfaceSet.to_file()` output and reads it back with `from_file()`.

## Control Flow
The test embeds reference-policy interface text with `interface(...)`, `gen_require`, `allow`, `optional_policy`, `tunable_policy`, and nested interface calls. It parses text through `refparser.parse()`, then `InterfaceSet.add_headers()` extracts and expands access data. Export writes to a local file named `output`, then reimports and checks expected interface names.

## State And Persistence
Most state is in memory within `InterfaceSet.interfaces`, each interface's `.access` and `.params`. `test_export()` persists a temporary `output` file in the test directory, which the Makefile cleans.

## Dependencies And Integration Points
It depends on `sepolgen.access`, `sepolgen.interfaces`, `sepolgen.policygen`, `sepolgen.refparser`, and `sepolgen.refpolicy`. The parser dependency indirectly exercises `yacc.py`. The exported interface data is also consumed by matching and CLI tooling.

## Risks And Edge Cases
String snippets include optional and tunable policy blocks but assertions mostly focus on allow rules and interface names, so conditional-policy semantics are not deeply validated. The export test only checks names after round-trip, not full access vectors or parameter metadata. File output is fixed-name and working-directory dependent.

## Test Signals
This is the strongest test signal for interface expansion and parameter inference. It confirms nested calls substitute parameters correctly and duplicate/no-op calls do not unexpectedly add access.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_interfaces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_matching.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_matching.py

## Purpose
This file tests the ranking containers used to match access vectors against reference-policy interfaces. It also contains a minimal smoke path for `AccessMatcher.search_ifs()`.

## Important Tests And Exercised APIs
`TestMatch` validates `matching.Match` equality and ordering by distance and information-flow direction-change flags. `TestMatchList` validates threshold handling, the `bastards` collection for weak/disallowed matches, sorting, and `best()`.

`AccessMatcher.test_search()` parses embedded interface text, builds an `InterfaceSet`, creates an access vector, and invokes `matching.AccessMatcher().search_ifs(...)` with a `MatchList`, but it has no assertions after the call.

## Control Flow
The ranking tests construct `Match` objects manually and append them to `MatchList`. The access matcher smoke test follows the same parser and interface expansion path as `test_interfaces.py`, then exercises matching search code.

## State And Persistence
All state is in memory: `Match.dist`, `Match.info_dir_change`, `MatchList.threshold`, `allow_info_dir_change`, and `bastards`.

## Dependencies And Integration Points
It imports `sepolgen.matching`, `sepolgen.refparser`, `sepolgen.interfaces`, and `sepolgen.access`. The smoke test integrates parser output, interface expansion, access vectors, and matching search.

## Risks And Edge Cases
The most important integration call has no assertions, so regressions in match quality or result contents could pass as long as no exception is raised. The name `bastards` is an internal compatibility detail that tests couple to directly. Threshold and direction-change logic are covered only with a few scalar examples.

## Test Signals
Useful signals exist for ordering and threshold bucketing. Search behavior is only a smoke signal and should not be treated as comprehensive matching validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_matching.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_module.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_module.py

## Purpose
This file tests that `sepolgen.module.ModuleCompiler` can produce a compiled SELinux policy package from a `.te` fixture under both explicit and instance-configured refpolicy modes.

## Important Tests And Exercised APIs
`TestModuleCompiler.test()` creates a `ModuleCompiler`, calls `create_module_package("module_compile_test.te", refpolicy=True)`, verifies `module_compile_test.pp` exists with `os.stat()`, deletes it, then sets `mc.refpolicy = True` and calls `create_module_package(..., refpolicy=False)` to verify instance state is honored.

## Control Flow
The test is linear and file-system based. It delegates all real compilation behavior to `ModuleCompiler`, then checks only for the package artifact.

## State And Persistence
It creates and removes `module_compile_test.pp`. The tests Makefile also cleans `.fc`, `.if`, `.pp`, and related temporary outputs because the compiler may generate more than the package in failure or intermediate paths.

## Dependencies And Integration Points
It depends on a local `module_compile_test.te` fixture and on external SELinux policy compilation tools used by `ModuleCompiler`. It imports `os` for artifact checks and removal.

## Risks And Edge Cases
The test can fail in environments without SELinux build tooling even if Python code is correct. It checks artifact existence only, not package content or compiler command diagnostics. Fixed filenames make concurrent test execution unsafe in the same directory.

## Test Signals
This is an integration smoke test for module compilation and refpolicy flag handling. It provides little granularity for diagnosing compilation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_module.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_objectmodel.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_objectmodel.py

## Purpose
This file tests permission mapping loading and default behavior in `sepolgen.objectmodel.PermMappings`.

## Important Tests And Exercised APIs
`TestInfoFlow.test_from_file()` constructs `PermMappings`, opens local `perm_map`, loads it with `from_file()`, then checks `get("filesystem", "mount")` returns a mapping with permission `mount`, write-flow direction, and weight `1`. It verifies missing known-class permissions raise `KeyError`, while `getdefault()` returns default mappings with both-direction flow and weight `5`.

## Control Flow
The test reads the permission map fixture, performs one concrete lookup, one failing lookup, and two default lookups.

## State And Persistence
State is the in-memory permission map loaded from `perm_map`. The file is read only.

## Dependencies And Integration Points
It depends on `sepolgen.objectmodel` and the local `perm_map` data file. This data corresponds to the shared file installed by `src/share/Makefile`.

## Risks And Edge Cases
The test assumes the current working directory contains `perm_map`. It validates only one real mapping from the fixture, so broad format regressions may escape unless they affect loading or the checked entry.

## Test Signals
It gives a targeted signal for permission-map parsing, lookup failure, and fallback defaults used by information-flow or matching logic.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_objectmodel.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_policygen.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_policygen.py

## Purpose
This file tests conversion from access vectors into reference-policy module rules by `sepolgen.policygen.PolicyGenerator`, including optional extended-permission rule generation.

## Important Tests And Exercised APIs
`test_init()` verifies `PolicyGenerator.xperms` defaults to false. `test_set_gen_xperms()` checks toggling extended-permission generation. `test_av_rules()` builds three same-source/same-target file permissions and asserts `add_access()` emits one `refpolicy.AVRule` with sorted permissions in the module.

`test_ext_av_rules()` enables xperms, builds file and dir ioctl access vectors with `XpermSet` values, adds them to an `AccessVectorSet`, and verifies the module contains both plain `AVRule` and `AVExtRule` objects per class with correct source, target, class, operation, rule type, and merged ranges.

## Control Flow
Each test creates access vectors and an `AccessVectorSet`, calls `PolicyGenerator.add_access()`, then inspects `self.g.module.children`. The xperm test manually classifies resulting children by type and object class because rule ordering is not assumed.

## State And Persistence
State lives in the `PolicyGenerator` instance and its in-memory module tree. No files are written by these tests.

## Dependencies And Integration Points
It depends on `sepolgen.policygen`, `sepolgen.access`, and `sepolgen.refpolicy`. It validates the downstream consumer of audit/access-vector generation and upstream producer of SELinux policy source rules.

## Risks And Edge Cases
The plain AV rule test asserts an exact string, so it relies on deterministic permission ordering. The xperm test is more robust about rule ordering but still assumes class partitioning is unambiguous. It does not test dontaudit, interface generation, module headers, or full policy serialization.

## Test Signals
The file provides strong signals for plain allow generation and ioctl xperm generation, including range merging and separation by object class.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_policygen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_refparser.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_refparser.py

## Purpose
This file is a minimal parser smoke test for reference-policy interface syntax. It feeds a multi-interface reference-policy snippet through `sepolgen.refparser.parse()`.

## Important Tests And Exercised APIs
`TestParser.test_interface_parsing()` embeds three `interface(...)` definitions with summary/param comments, `gen_require`, `allow` rules, `typeattribute`, conditionals, optional policy, tunable policy, and interface calls. The test calls `refparser.parse(interface_example)`.

## Control Flow
The parser result is assigned to `h`, and the rest of the detailed assertions are commented out. The test therefore passes if parsing completes without exception.

## State And Persistence
All state is in memory. The parser may generate yacc table/debug artifacts depending on parser configuration and working directory, which the tests Makefile cleans.

## Dependencies And Integration Points
It imports `sepolgen.refparser` and `sepolgen.refpolicy`. It indirectly depends on yacc/lex parser generation and grammar action code.

## Risks And Edge Cases
Because all semantic assertions are commented, malformed parse trees could pass. The test still catches syntax-level parser regressions for a representative interface sample, but it is not a structural parser test.

## Test Signals
This is a parser smoke signal. `test_interfaces.py` supplies stronger semantic validation for parsed interface data.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_refparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_refpolicy.py -->
# sources/security-integrity/selinux/python/sepolgen/tests/test_refpolicy.py

## Purpose
This file tests core reference-policy model objects: identifier sets, extended permission sets, SELinux security contexts, object classes, AV rules, extended AV rules, type rules, parse tree nodes, and headers iteration.

## Important Tests And Exercised APIs
`TestIdSet` verifies compact versus braced space string formatting. `TestXpermSet` validates initialization, private range normalization, add/extend merging, complement formatting, single values, multi-values, and ranges. `TestSecurityContext` validates context parsing, MLS default behavior via `selinux.is_selinux_mls_enabled()`, explicit default levels, invalid context handling, and equality.

`TestObjectClass`, `TestAVRule`, `TestAVExtRule`, and `TestTypeRule` validate model initialization and string serialization. `AVExtRule.from_av()` is tested for normal target and self-target conversion. `TestParseNode` constructs a small tree but does not assert traversal output. `TestHeaders` checks iteration over all children and only interfaces.

## Control Flow
Tests mostly instantiate model objects, mutate public sets/fields, call formatting or conversion methods, and assert exact strings or object fields. Some set-order-sensitive checks are normalized by splitting and sorting.

## State And Persistence
All state is in memory. One test consults live SELinux MLS state through the `selinux` Python binding, making expected context string output environment-sensitive.

## Dependencies And Integration Points
It depends on `sepolgen.refpolicy`, `sepolgen.access`, and the external `selinux` Python module. The tested objects are central integration points for access parsing, policy generation, interface expansion, and audit conversion.

## Risks And Edge Cases
`TestParseNode.test_walktree()` lacks assertions and is currently only a construction smoke test. Some serialization expectations depend on set formatting implementation. Environment-dependent MLS behavior can produce different expected strings depending on the host SELinux configuration.

## Test Signals
This is a broad unit signal for the policy model layer, especially xperm range normalization and rule string generation. It does not deeply validate tree walking semantics despite constructing parse nodes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolgen/tests/test_refpolicy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/Makefile -->
# sources/security-integrity/selinux/python/sepolicy/Makefile

## Purpose
This Makefile builds, tests, and installs the `sepolicy` Python command package and CLI wrapper. It also installs man pages and bash completion, and creates the compatibility `sepolgen` symlink.

## Important Targets And Variables
`PYTHON ?= python3`, `PREFIX ?= /usr`, `BINDIR`, `MANDIR`, and `BASHCOMPLETIONDIR` define build/install paths. `python-build` runs `$(PYTHON) -m build --no-isolation --wheel .`. `install` builds a wheel, force-reinstalls it with pip under `$(PREFIX)` and optional `DESTDIR`, installs `sepolicy.py` as `$(BINDIR)/sepolicy`, creates `sepolgen -> sepolicy`, installs man pages including localized `$(LINGUAS)` subdirectories, and installs completion as `sepolicy`.

`clean` removes Python build outputs, egg metadata, backups, and bytecode. `test` runs `test_sepolicy.py -v`. `sepolgen` creates only the symlink in the current directory. `relabel` is an empty placeholder.

## Control Flow
Build flow is wheel-based. Install flow combines Python packaging with manual CLI/man/completion installation. The pip command conditionally emits `--root $(DESTDIR) --ignore-installed --no-deps` only when `DESTDIR` is non-empty.

## State And Persistence
Persistent outputs include `build/`, `dist/`, egg-info during build, installed Python package files, `/usr/bin/sepolicy` by default, a `sepolgen` symlink, man pages, and bash completion. Local `clean` removes build state but not installed state.

## Dependencies And Integration Points
It depends on Python build tooling, pip, wheel metadata in the directory, man page files matching `*.8`, optional localized man page directories, and `sepolicy-bash-completion.sh`. The installed CLI wrapper executes `sepolicy.py`.

## Risks And Edge Cases
`CFLAGS` is set and extended but this Makefile path is mostly Python packaging; its relevance depends on package build internals. The `install` rule force-reinstalls from `dist/*.whl`, which can be ambiguous if multiple wheels remain. There is no uninstall target. The symlink name means invoking the same script as `sepolgen` changes default CLI behavior in `sepolicy.py`.

## Test Signals
The only test target runs `test_sepolicy.py`, not included in this subset. Successful installation should be validated by command execution, man page presence, and completion loading.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy-bash-completion.sh -->
# sources/security-integrity/selinux/python/sepolicy/sepolicy-bash-completion.sh

## Purpose
This bash completion script provides dynamic completions for the `sepolicy` CLI. It completes subcommands, common options, SELinux domains, booleans, classes, users, port types, policy paths, and filesystem paths using installed SELinux query tools and sepolgen interface metadata.

## Important Functions
Helper functions include `__contains_word`, `__get_all_paths`, `__get_all_ftypes`, `__get_all_networks`, `__get_all_booleans`, `__get_all_types`, `__get_all_admin_interfaces`, `__get_all_user_role_interfaces`, `__get_all_user_domains`, `__get_all_users`, `__get_all_classes`, `__get_all_port_types`, `__get_all_domain_types`, and `__get_all_domains`.

`_sepolicy()` is the completion dispatcher. It determines the current verb from `COMP_WORDS`, offers top-level verbs and common options, then branches for `booleans`, `communicate`, `generate`, `interface`, `manpage`, `network`, and `transition`. It uses `COMPREPLY`, `compgen`, and `compopt -o filenames` for file/directory completions. The script registers `complete -F _sepolicy sepolicy`.

## Control Flow
At completion time, `_sepolicy` inspects `COMP_WORDS[1]`, current and previous words, and scans for a recognized verb not treated as an option argument. Without a verb it completes verbs or policy files after `-P/--policy`. With a verb it completes option names or context-specific argument values based on `prev`.

## State And Persistence
No persistent state is written. Runtime state is shell-local variables and `COMPREPLY`. Dynamic candidate lists are read from commands and files at completion time.

## Dependencies And Integration Points
It depends on bash completion internals, `seinfo`, `getsebool`, `awk`, `sed`, `tail`, `dir`, `grep`, `cut`, `/var/lib/sepolgen/interface_info`, and the installed SELinux policy environment. It mirrors the subcommands and many options defined by `sepolicy.py`.

## Risks And Edge Cases
The option lists contain apparent typos or drift, such as `-all` rather than `--all` in some entries, duplicate `-u --list_user`, `-i --interface` while the Python parser uses `--interfaces`, and missing newer options such as `manpage --source_files`. Several helper functions parse command output with simple text filters that may be fragile across tool versions. `for w in $*` and unquoted command substitutions can split values on whitespace.

## Test Signals
No tests are present in this subset. Manual signals are successful completion for every `sepolicy.py` subcommand and no stderr noise when SELinux tools are absent or policy data is unavailable.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy-bash-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy.py -->
# sources/security-integrity/selinux/python/sepolicy/sepolicy.py

## Purpose
This is the executable `sepolicy` CLI and compatibility entry point for `sepolgen`. It exposes policy inspection, generation, manpage creation, network queries, boolean descriptions, interface listing, transition analysis, communication analysis, and a GUI launcher through argparse subcommands.

## Important APIs, Classes, And Functions
Validation actions subclass `argparse.Action`: `CheckPath`, `CheckType`, `CheckBoolean`, `CheckDomain`, `CheckClass`, `CheckAdmin`, `CheckPort`, `CheckPortType`, `LoadPolicy`, `CheckUser`, `CheckRole`, and `InterfaceInfo`. These convert or validate CLI arguments against live policy data and store normalized values on the argparse namespace.

Command handlers include `network()`, `gui_run()`, `manpage()`, `communicate()`, `booleans()`, `transition()`, `interface()`, and `generate()`. Each has a corresponding `gen_*_args()` function that registers parser arguments. Utility functions include `generate_custom_usage()`, `port_string_to_num()`, `_print_net()`, `manpage_work()`, and `print_interfaces()`.

The `__main__` block creates the top-level parser, registers all subcommands, supports `-P/--policy` via `LoadPolicy`, rewrites invocation as `sepolgen` to `generate`, parses arguments, calls `args.func(args)`, and maps `ValueError`, `IOError`, and `KeyboardInterrupt` to process exits.

## Control Flow
Startup imports SELinux and sepolicy modules, installs gettext fallback `_`, and defines custom usage for `sepolicy generate`. Argument generation builds subparsers for booleans, communicate, generate, gui, interface, manpage, network, and transition.

`network()` builds port dictionaries, handles mutually exclusive list/port/type/domain/application queries, resolves application init transition types into domains, and prints bind/connect permissions through `_print_net()`. `manpage()` optionally loads an alternate-root policy, selects all or requested domains, uses a multiprocessing pool with fork start method to run `manpage_work()`, and optionally emits HTML index pages. `generate()` validates policy type combinations, derives a name from application command when needed, configures a `sepolicy.generate.policy` object, adds write paths/domains/users/admin roles, and prints generated output paths.

`interface()` lists admin, user-role, all, or selected interfaces and can print verbose formatted information or run compile tests. `communicate()`, `booleans()`, and `transition()` are thinner wrappers around sepolicy library calls.

## State And Persistence
The script mutates process policy state when `LoadPolicy` calls `sepolicy.policy(values)` and when `manpage()` loads an alternate-root policy. `generate()` writes policy template files through the `sepolicy.generate.policy.generate()` call. `manpage()` writes man pages and optional HTML to `args.path`. `gui_run()` opens GUI state externally. Global `all_classes` caches class names after first validation.

## Dependencies And Integration Points
It depends on the Python `selinux` binding, the `sepolicy` Python package, optional submodules `sepolicy.gui`, `sepolicy.manpage`, `sepolicy.network`, `sepolicy.communicate`, `sepolicy.transition`, `sepolicy.interface`, and `sepolicy.generate`, plus multiprocessing. It integrates with installed SELinux policy, `/sys/fs/selinux/policy` by default, alternate policy files, generated manpage content, and the Makefile-installed `sepolicy`/`sepolgen` entry points.

## Risks And Edge Cases
Several argparse actions raise `ValueError` rather than `argparse.ArgumentError`, so errors are caught only after top-level parse handling and may produce less standard argparse output. `CheckPort` allows values up to `65536`, although valid TCP/UDP ports normally end at `65535`. `CheckRole` strips the final two characters from a role value, assuming a `_r` suffix without validating that suffix. `generate()` defines command policy types with `--init` defaulting `policytype` to daemon, which means default interactions around omitted policy types require careful testing.

`manpage()` unconditionally calls `multiprocessing.set_start_method('fork')`, which can raise if a start method was already set in an embedding process. Multiprocessing propagates worker exceptions only when `result.get()` is called. Many commands depend on live SELinux policy data and optional packages, so behavior is environment-sensitive.

## Test Signals
This subset does not include `test_sepolicy.py`; the Makefile refers to it as the main test target. Indirect validation should cover parser setup for every subcommand, argument validation against mocked or fixture policy data, generated policy output paths, manpage parallelism, network formatting, and `sepolgen` symlink invocation behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/sepolicy/sepolicy.py -->
