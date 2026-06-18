# subset-b-006312 Research

Grouped code research for the Ceph client Rust kernel XArray wrapper, Rust-for-Linux procedural macros, the standalone `pin-init` library and proc macros, `pin-init` examples, and vendored `proc-macro2` fallback support. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/xarray.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/xarray.rs

## Purpose
`xarray.rs` provides a Rust ownership wrapper around Linux's C `struct xarray`. It stores sparse integer-indexed entries whose ownership is represented by `ForeignOwnable`, exposes lock-guarded lookup/mutation/removal/store operations, and destroys all live entries when the array is dropped.

## Important APIs, Types, And Functions
The main public type is `XArray<T: ForeignOwnable>`, initialized through `XArray::new(AllocKind) -> impl PinInit<Self>`. `AllocKind::{Alloc, Alloc1}` selects `XA_FLAGS_ALLOC` or `XA_FLAGS_ALLOC1`. Access is mediated by `Guard<'_, T>`, returned from `try_lock()` or `lock()`, with `get()`, `get_mut()`, `remove()`, and `store()`. `StoreError<T>` carries both the kernel `Error` and the value that could not be inserted.

## Control Flow
Creation uses `pin_init!` and `Opaque::ffi_init` to call `xa_init_flags`. Destruction iterates over all present entries using `xa_find` followed by `xa_find_after`, converts each foreign pointer back into an owned `T`, drops it, then calls `xa_destroy`. Runtime access first takes the xarray spinlock through `xa_lock` or `xa_trylock`; `Guard::drop` releases it with `xa_unlock`. `store()` converts a value with `T::into_foreign`, calls `__xa_store`, checks `xa_err`, returns the old value on success, and reconstructs the new value on failure.

## State And Persistence
State is entirely in the embedded C `xarray` plus type-level ownership invariants. Entries are either `XA_ZERO_ENTRY` or pointers returned by `T::into_foreign`; normal xarray APIs make zero entries appear as null on retrieval. There is no persistence beyond the lifetime of the `XArray`; dropping the wrapper reclaims all stored foreign-owned objects.

## Dependencies And Integration Points
The file depends on kernel bindings for `xa_*`, the kernel allocator flags wrapper, `ForeignOwnable` conversion traits, `Opaque`, `NotThreadSafe`, `build_assert!`, and `pin-init` macros. It is a kernel-safe collection primitive for Rust code that needs Linux xarray behavior while preserving Rust ownership and pin initialization conventions.

## Risks And Edge Cases
The correctness boundary is pointer ownership: any pointer inserted must have come from `T::into_foreign`, and every removed or overwritten pointer must be converted exactly once. `store()` requires `T::FOREIGN_ALIGN >= 4` because xarray uses low pointer bits internally. The guard is explicitly not thread-safe/sendable, and methods assume the xarray lock is held. Dropping while external references exist would violate invariants, so users must respect normal Rust ownership of the wrapper.

## Test Signals
Useful signals include the doctest-style insert/get/get_mut/overwrite/remove flow, allocation-failure injection for `__xa_store`, lock contention behavior for `try_lock`, drop leak checks for multiple stored values, and KASAN/Miri-style checks that overwrite and remove paths do not double-free or lose ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/xarray.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/concat_idents.rs -->
# sources/distributed-fs/ceph-client/rust/macros/concat_idents.rs

## Purpose
This file implements the kernel `concat_idents!` procedural macro helper. It concatenates exactly two identifiers and emits one identifier whose span is taken from the second argument for better diagnostics at the call site.

## Important APIs, Types, And Functions
`Input` parses `a, b` as two `proc_macro2::Ident` values separated by a comma. `concat_idents(Input)` formats the two identifiers together, constructs a new `Ident` with `b.span()`, and returns it as a single-token `TokenStream`.

## Control Flow
The macro entry point in `macros/lib.rs` parses user input into `Input`. This helper performs no semantic lookup; it only joins token spellings. Invalid arity or non-ident tokens are rejected by `syn::Parse` before concatenation.

## State And Persistence
No runtime or persistent state is kept. All state is temporary parser output and a single emitted token stream.

## Dependencies And Integration Points
It depends on `proc_macro2` token types and `syn` parsing. It is re-exported through the `#[proc_macro] pub fn concat_idents` entry point and is intended for Rust kernel macro code that needs generated names.

## Risks And Edge Cases
Because it formats identifiers as strings, raw identifiers and hygiene need care. The span intentionally comes from the second identifier, so diagnostics point at the caller-provided suffix rather than the prefix. The helper only supports two identifiers; more complex pasting is handled by `paste.rs`.

## Test Signals
Useful tests cover successful prefix/suffix concatenation, malformed input, punctuation or literal rejection, raw identifier behavior, and diagnostics span placement on generated identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/concat_idents.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/export.rs -->
# sources/distributed-fs/ceph-client/rust/macros/export.rs

## Purpose
`export.rs` implements the `#[export]` procedural attribute for Rust functions that C code calls through bindgen-generated kernel bindings. It disables Rust name mangling and emits a compile-time signature compatibility check against the C declaration.

## Important APIs, Types, And Functions
The only helper is `export(f: syn::ItemFn) -> TokenStream`. It extracts `f.sig.ident`, references `::kernel::bindings::<name>`, and emits the original function with `#[no_mangle]`.

## Control Flow
The generated `const _: ()` block contains an `if true { bindings::name } else { name }` expression. Rust type-checks both branches, so the Rust function must match the bindgen declaration. After the check, the original item is emitted with `#[no_mangle]`.

## State And Persistence
No runtime state exists. The output affects the compiled symbol table and compile-time type checking only.

## Dependencies And Integration Points
It integrates with `macros/lib.rs` as `#[proc_macro_attribute] export`, `quote`, `syn::ItemFn`, and `::kernel::bindings`. It is complementary to, but distinct from, Linux `EXPORT_SYMBOL_*`; Rust symbols are currently exported elsewhere.

## Risks And Edge Cases
The macro assumes the Rust function name exactly matches a generated binding. Missing bindings or signature drift fail at compile time. It should not be used for functions called through vtables or function pointers, because those contracts are checked differently.

## Test Signals
Tests should include matching and mismatching C/Rust signatures, missing bindgen declarations, generated `#[no_mangle]` symbol inspection, and confirming the macro rejects non-function input at the public entry point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/export.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/fmt.rs -->
# sources/distributed-fs/ceph-client/rust/macros/fmt.rs

## Purpose
`fmt.rs` implements a formatting helper used by kernel logging macros. It wraps every formatting argument in `::kernel::fmt::Adapter` so kernel-specific formatting behavior is applied while preserving `core::format_args!` syntax.

## Important APIs, Types, And Functions
The public crate-internal entry is `fmt(input: TokenStream) -> TokenStream`. It scans the first literal format string for named placeholders, stores names in a `BTreeSet`, rewrites explicit positional or named arguments through `Adapter(&(expr))`, and appends implicit named arguments that appeared only in the format string.

## Control Flow
If the first token is not a string literal, the macro returns the input unchanged. Otherwise it parses `{name}` patterns while skipping escaped `{{`, ignoring numeric positional placeholders, and stripping format specifiers after `:`. It then walks remaining tokens, splitting on commas, and for each argument separates an optional `lhs =` from the expression so named arguments remain named. At the end it emits `::core::format_args!(...)`.

## State And Persistence
All state is transient: a set of inferred placeholder names plus token-stream accumulators. There is no runtime storage.

## Dependencies And Integration Points
It depends on `proc_macro2`, `quote_spanned`, and the kernel `fmt::Adapter`. `macros/lib.rs` exposes it as `fmt!`, and higher-level logging macros use it to adapt arguments before printing.

## Risks And Edge Cases
The format-string scanner is intentionally lightweight and does not implement the full Rust format grammar. It can miss or misinterpret unusual formatting constructs, although actual `format_args!` still performs final validation. Argument splitting on top-level comma tokens relies on the token stream structure and preserves `a = b = c` by splitting only the first equals sign. Span selection uses the format literal span for generated adapter references.

## Test Signals
Tests should cover positional arguments, explicit named arguments, implicit captured names, escaped braces, format specifiers, assignments inside expressions, non-literal first tokens, and ensuring all generated values are wrapped exactly once in `Adapter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/fmt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/helpers.rs -->
# sources/distributed-fs/ceph-client/rust/macros/helpers.rs

## Purpose
`helpers.rs` contains shared utilities for the Rust kernel procedural macros: ASCII-only string literal parsing, proc-macro source file discovery, and cfg-attribute filtering.

## Important APIs, Types, And Functions
`AsciiLitStr` wraps `syn::LitStr`, implements `Parse`, `ToTokens`, and `value()`, and rejects non-ASCII strings. `file()` returns the current call-site source file using either `Span::source_file().path()` or stable `Span::file()` depending on `CONFIG_RUSTC_HAS_SPAN_FILE`. `gather_cfg_attrs()` filters attributes to `#[cfg(...)]`.

## Control Flow
`AsciiLitStr::parse` reads a literal and validates `value().is_ascii()`. `file()` compiles one of two span APIs using cfg flags. `gather_cfg_attrs` is a simple iterator adapter used by macros that need to propagate cfg gates to generated items.

## State And Persistence
No persistent state is kept. The file provides parser wrappers and helpers only.

## Dependencies And Integration Points
It depends on `proc_macro`, `proc_macro2`, `quote`, and `syn`. `module.rs` uses `AsciiLitStr` for module metadata, `kunit.rs` uses `file()` for assertion source reporting, and `vtable.rs` uses `gather_cfg_attrs`.

## Risks And Edge Cases
ASCII validation prevents invalid kernel metadata strings but also rejects legitimate Unicode in fields that use `AsciiLitStr`. The `file()` helper depends on compiler feature cfgs matching the actual proc-macro API. `gather_cfg_attrs()` only preserves `cfg` attributes, not `cfg_attr`.

## Test Signals
Useful tests include ASCII and non-ASCII metadata literals, source-file path reporting under both compiler cfgs, and cfg propagation through vtable and KUnit-generated items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/helpers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/kunit.rs -->
# sources/distributed-fs/ceph-client/rust/macros/kunit.rs

## Purpose
`kunit.rs` converts an inline Rust test module annotated with `#[kunit_tests(name)]` into a Linux KUnit test suite. It preserves normal module items, wraps each `#[test]` function in an extern "C" KUnit case, and registers the suite only when `CONFIG_KUNIT="y"`.

## Important APIs, Types, And Functions
The central function is `kunit_tests(test_suite: Ident, module: ItemMod) -> Result<TokenStream>`. It emits per-test `kunit_rust_wrapper_<test>` functions, a static mutable `TEST_CASES` array terminated by `::pin_init::zeroed()`, and a `::kernel::kunit_unsafe_test_suite!` invocation. It also inserts local `assert!` and `assert_eq!` macro overrides that call `kernel::kunit_assert!` and `kernel::kunit_assert_eq!`.

## Control Flow
The helper validates that the suite name is no longer than 255 bytes and that the target module has inline contents. It gates the module with `#[cfg(CONFIG_KUNIT="y")]`, scans items, removes `#[test]` attributes from functions, and leaves non-test functions/items unchanged. For each test, it copies any `#[cfg]` attributes onto the wrapper call block, starts status as skipped, sets success before calling the Rust test, and asserts that the returned test result is OK.

## State And Persistence
Generated state is compile-time/static test registration data: wrappers and the mutable KUnit case array. Runtime state is KUnit's per-test status field and any state used by the test functions themselves.

## Dependencies And Integration Points
It depends on `syn`, `quote`, `CString`, `LitCStr`, `pin_init::zeroed`, `kernel::kunit` helpers, and `helpers::file()`. It integrates Rust unit-test syntax with Linux KUnit registration and status reporting.

## Risks And Edge Cases
Only inline modules are supported; `mod tests;` is rejected. Suite names over 255 bytes fail. The generated `static mut TEST_CASES` is required by KUnit registration and must not be accessed unsafely elsewhere. Local macro overrides are inserted before each test and may interact with user-defined macros in unusual scopes. Cfg-gated tests must have their cfgs propagated to avoid wrappers calling missing functions.

## Test Signals
Signals include macro expansion for modules with test and non-test items, cfg-gated tests, suite-name length rejection, KUnit-disabled builds, assertion macro behavior, generated C string names, and registration arrays terminated with a zeroed case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/kunit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/lib.rs -->
# sources/distributed-fs/ceph-client/rust/macros/lib.rs

## Purpose
`macros/lib.rs` is the procedural macro crate entry point for Rust-for-Linux kernel macros. It documents and exposes module declaration, vtable helpers, C export checking, logging-format adaptation, identifier concatenation/pasting, and KUnit suite registration.

## Important APIs, Types, And Functions
Public proc-macro entry points are `module!`, `#[vtable]`, `#[export]`, `fmt!`, `concat_idents!`, `paste!`, and `#[kunit_tests]`. The file also declares submodules `concat_idents`, `export`, `fmt`, `helpers`, `kunit`, `module`, `paste`, and `vtable`.

## Control Flow
Each entry point parses `proc_macro::TokenStream` input with `syn::parse_macro_input!` where applicable, delegates to the specialized helper module, converts `syn::Error` into compile errors, and returns the generated token stream. `paste!` directly converts to `proc_macro2`, recursively expands `[< ... >]` groups, and returns the rewritten stream.

## State And Persistence
The crate itself stores no runtime state. Its generated code can create module metadata sections, init/exit functions, statics, KUnit arrays, no-mangle symbols, and associated constants, but those are owned by the expanded caller.

## Dependencies And Integration Points
It depends on Rust proc-macro infrastructure, `syn`, `proc_macro2`, and the helper modules in the same crate. Generated code integrates with kernel crates such as `kernel`, `pin_init`, module parameter support, KUnit, and bindgen bindings.

## Risks And Edge Cases
Because this file is the public macro facade, documentation and parser behavior must stay aligned with helper modules. Feature gates (`extract_if`, `proc_macro_span`) are tied to Rust compiler/Kconfig support. Errors should become compile diagnostics rather than panics, except for internal helpers like `paste` that currently panic on malformed paste syntax.

## Test Signals
High-value coverage includes trybuild-style expansion tests for every public macro, docs examples, kernel build tests under module and built-in cfgs, compiler-version cfg combinations, and negative tests that check useful compile errors for malformed input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/module.rs -->
# sources/distributed-fs/ceph-client/rust/macros/module.rs

## Purpose
`module.rs` implements the `module!` macro that turns Rust module metadata and a module type into Linux module init/exit glue, `.modinfo` records, optional module parameter registration, and built-in initcall support.

## Important APIs, Types, And Functions
Important types are `ModuleInfo`, `Parameter`, and `ModInfoBuilder`. `module(info: ModuleInfo)` is the main generator. `param_ops_path()` maps supported Rust integer parameter types to kernel `PARAM_OPS_*` symbols. `parse_ordered_fields!` parses macro fields in arbitrary syntax order but enforces the documented order. `ModInfoBuilder::{emit, emit_param, emit_params}` builds `.modinfo` and `__param` static items.

## Control Flow
Parsing requires `type`, `name`, and `license`; optional fields include `authors`, `description`, `alias`, `firmware`, `imports_ns`, and `params`. Generation normalizes the module name into a Rust identifier, emits modinfo records for loadable and built-in variants, reads `RUST_MODFILE` for built-in `file=...`, emits module parameter access statics and `kernel_param` structures, creates `THIS_MODULE`, aliases the user type to `LocalModule`, implements `ModuleMetadata`, and emits double-nested private init/exit glue. Loadable modules expose `init_module` and `cleanup_module`; built-ins use an initcall section or PREL32 global asm plus unique init/exit symbols.

## State And Persistence
Generated persistent state includes `.modinfo` byte strings, parameter access statics, `__param` entries, `THIS_MODULE`, and a `static mut __MOD: MaybeUninit<LocalModule>`. Runtime state is initialized exactly once through `<LocalModule as InPlaceModule>::init(...).__pinned_init(__MOD.as_mut_ptr())` and later destroyed by `__MOD.assume_init_drop()` on successful module unload or built-in exit.

## Dependencies And Integration Points
The macro integrates tightly with Linux module metadata sections, initcall sections, module parameter ABI, `kernel::ThisModule`, `kernel::InPlaceModule`, `kernel::ModuleMetadata`, `pin_init::PinInit`, and `RUST_MODFILE`. It uses `CString` for NUL-terminated names and `AsciiLitStr` for metadata that must be ASCII.

## Risks And Edge Cases
Ordering validation can reject otherwise syntactically valid macro input. `param_ops_path()` panics for unsupported parameter types. Names containing NUL are rejected by `CString::new`; module names with hyphens are converted to underscores only for Rust identifiers. `static mut __MOD` relies on kernel lifecycle guarantees that init and exit are called at most once and in order. Architecture-specific PREL32 initcall emission must match kernel linker expectations.

## Test Signals
Tests should cover full metadata emission, built-in versus loadable cfg output, parameter declarations for every supported integer type, wrong field order and duplicate/unknown field diagnostics, missing `RUST_MODFILE`, hyphenated module names, init failure cleanup behavior, and generated symbol/section inspection in kernel builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/module.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/paste.rs -->
# sources/distributed-fs/ceph-client/rust/macros/paste.rs

## Purpose
`paste.rs` implements a small identifier-pasting macro similar to the `paste` crate, limited to identifiers and literals inside `[< ... >]` groups. It supports case modifiers and span selection for generated identifiers.

## Important APIs, Types, And Functions
`expand(tokens: &mut Vec<TokenTree>)` is the recursive entry. `concat()` creates one identifier from a bracket group. `concat_helper()` walks paste segments and returns string/span pairs. Supported modifiers are `:span`, `:lower`, and `:upper`.

## Control Flow
Expansion recursively descends into groups. A bracket group whose first token is `<` and last token is `>` is replaced by a concatenated `Ident`; all other groups are recursively expanded and rebuilt with the original delimiter/span. After recursion, a reverse pass removes invisible delimiter groups adjacent to `::` path separators because path segments cannot contain such groups.

## State And Persistence
No state persists outside the token vector being rewritten. Span state is local to a paste group; the `span` modifier may select one segment span as the generated identifier span.

## Dependencies And Integration Points
It depends only on `proc_macro2` token types. `macros/lib.rs` exposes it as `paste!` for kernel macro authors who need generated identifiers without depending on the full external `paste` crate behavior.

## Risks And Edge Cases
Malformed paste syntax causes panics rather than structured `syn::Error` diagnostics. The implementation strips quotes from string literals and `r#` from raw identifiers before concatenation. It does not support lifetimes or doc-string concatenation. Only ASCII-ish identifier validation is left to `Ident::new`, so invalid pasted names fail there.

## Test Signals
Useful tests include nested group expansion, literals plus identifiers, raw identifiers, lower/upper/span modifiers, duplicate `span` modifier rejection, invisible group removal around paths, and malformed token negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/paste.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/vtable.rs -->
# sources/distributed-fs/ceph-client/rust/macros/vtable.rs

## Purpose
`vtable.rs` implements `#[vtable]`, which lets Rust traits model Linux C vtables where optional methods are represented by null function pointers. It generates `HAS_*` associated constants that indicate which optional methods an implementation actually overrides.

## Important APIs, Types, And Functions
`vtable(input: Item) -> Result<TokenStream>` dispatches to `handle_trait(ItemTrait)` or `handle_impl(ItemImpl)`. Trait handling adds `USE_VTABLE_ATTR` and default `HAS_METHOD = false` constants. Impl handling adds `USE_VTABLE_ATTR` and `HAS_METHOD = true` constants for implemented methods unless the user already defined the constant.

## Control Flow
On traits, every trait method produces a cfg-preserving `HAS_*` bool constant. On impl blocks, explicitly defined constants are first collected to allow overrides, then each implemented method produces a cfg-preserving `HAS_* = true` constant. Applying the attribute to anything other than a trait or impl emits an error.

## State And Persistence
No runtime state is stored. Generated associated constants become compile-time signals consumed by vtable construction code elsewhere.

## Dependencies And Integration Points
It uses `syn`, `quote::ToTokens`, `HashSet`, and `helpers::gather_cfg_attrs`. It integrates with kernel traits that generate C vtables and with default methods that should never be called directly when optional.

## Risks And Edge Cases
Method names are uppercased mechanically, so unusual names or cfg combinations must be consistent between trait and impl. Required methods and optional methods both receive constants at the trait site because the impl site cannot distinguish them. Users can override generated constants, which is intentional but can lie if misused.

## Test Signals
Tests should cover trait annotation, impl annotation, cfg propagation, explicit `HAS_*` override, invalid target items, and integration with a C-vtable builder that chooses null pointers based on constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/macros/vtable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/big_struct_in_place.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/big_struct_in_place.rs

## Purpose
This example demonstrates why `pin-init` supports in-place construction: a `BigStruct` with a 1 GiB array can be initialized directly in heap memory without first materializing the whole value on the stack.

## Important APIs, Types, And Functions
`BigStruct` contains a 1 GiB `buf`, scalar fields, and a `ManagedBuf`. `ManagedBuf::new()` returns `impl Init<Self>` using `init!(ManagedBuf { buf <- init_zeroed() })`. `main()` uses `Box::init(init!(BigStruct { ... }))` when `std` or `alloc` is available.

## Control Flow
The initializer zeroes the big array in place, writes scalar fields, initializes `managed_buf` through its own initializer, allocates the final `Box`, and prints the size of the initialized value. No stack-sized temporary `BigStruct` is constructed.

## State And Persistence
State lives only in the allocated `Box<BigStruct>` during `main`. The example has no external persistence.

## Dependencies And Integration Points
It depends on `pin_init::*`, the `alloc`/`std` features for `Box::init`, and `init_zeroed()`. It is a documentation and regression signal for large in-place initialization.

## Risks And Edge Cases
The huge allocation can fail or be unsuitable for constrained test environments. The example is feature-gated for allocation support, so no meaningful work happens without `std` or `alloc`. It mainly tests stack avoidance rather than business logic.

## Test Signals
Useful signals are successful run without stack overflow, allocation-failure behavior, correct reported size, and ensuring code generation does not create large stack temporaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/big_struct_in_place.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/error.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/error.rs

## Purpose
`error.rs` defines a tiny example error type used by other `pin-init` examples to unify infallible and allocation-failure paths.

## Important APIs, Types, And Functions
`pub struct Error` is a marker error. It implements `From<Infallible>` by matching the impossible value and, under `alloc`, implements `From<AllocError>` by returning `Error`.

## Control Flow
There is no substantive control flow beyond conversion implementations. The dead-code `main()` only creates the type.

## State And Persistence
The error type has no fields and carries no persistent state.

## Dependencies And Integration Points
It depends on `core::convert::Infallible` and optionally `std::alloc::AllocError`. Other examples import it where `? Error` initializers need an error type that can absorb allocation or impossible errors.

## Risks And Edge Cases
Because it is fieldless, it discards detailed allocation error context. That is acceptable for examples but not a rich production error model.

## Test Signals
Tests can compile examples that convert `Infallible` and `AllocError` into this type and verify feature-gated allocation conversions compile only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/linked_list.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/linked_list.rs

## Purpose
This example implements an intrusive circular doubly linked list node that must not move after insertion. It demonstrates `#[pin_data(PinnedDrop)]`, self-referential initialization with `&this in`, and pinned drop unlinking.

## Important APIs, Types, And Functions
`ListHead` has `next`, `prev`, and a pinned `PhantomPinned` field. `ListHead::new()`, `insert_next()`, and `insert_prev()` return `impl PinInit<Self>`. `next()` returns the next node unless the list is self-referential, and `size()` walks the circular list. `PinnedDrop for ListHead` unlinks a node on drop. `Link(Cell<NonNull<ListHead>>)` stores mutable raw links and provides `next`, `prev`, `replace`, `set`, and pointer access helpers.

## Control Flow
Initialization uses `pin_init!(&this in Self { ... })` to create self-links or splice a new node next to an existing list node. Insertion updates neighboring links by replacing `Cell` contents while creating the new node fields. Drop checks whether the node is linked to another node and, if so, updates adjacent `prev`/`next` links to bypass the dropped node.

## State And Persistence
State is in per-node `Cell<NonNull<ListHead>>` pointers. The list exists only in memory and relies on pinning to keep stored addresses valid. Dropping a node mutates neighboring nodes to maintain the circular list invariant.

## Dependencies And Integration Points
It depends on `pin_init`, `NonNull`, `Cell`, `PhantomPinned`, and the example `Error` type. Other examples, especially `mutex.rs`, reuse `ListHead` as a wait-list primitive.

## Risks And Edge Cases
The linked list uses unsafe raw pointers and assumes all nodes remain pinned and alive while linked. Incorrect insertion or premature drop can corrupt neighbors. `Cell` allows mutation through shared references, so external synchronization is the caller's responsibility. `size()` can loop forever if the circular invariant is broken.

## Test Signals
Signals include inserting stack- and heap-pinned nodes in several positions, dropping middle nodes, walking list order, validating `size()`, and running under Miri or sanitizers to catch dangling links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/linked_list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/mutex.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/mutex.rs

## Purpose
`mutex.rs` is a user-space-style example of a pinned mutex built from a spinlock, an intrusive wait list, and `UnsafeCell` data. It demonstrates initializing pinned subfields and using pinned stack wait entries.

## Important APIs, Types, And Functions
`SpinLock` wraps `AtomicBool` and returns `SpinLockGuard`. `CMutex<T>` is `#[pin_data]` with pinned `wait_list` and `data`. `CMutex::new(val: impl PinInit<T>)` returns `impl PinInit<Self>`, `lock()` returns `Pin<CMutexGuard<'_, T>>`, and `get_data_mut()` gives mutable access from `Pin<&mut Self>`. `CMutexGuard` implements `Drop`, `Deref`, and `DerefMut`. `WaitEntry` stores a pinned list node and, under `std`, the parked thread.

## Control Flow
Lock acquisition takes the spinlock. If already locked, it stack-pin-initializes a `WaitEntry` into the wait list, drops the spinlock while waiting, parks the thread under `std`, and retries until the mutex is available. Once acquired it sets `locked = true` and returns a pinned guard. Guard drop takes the spinlock, clears `locked`, unparks the first waiter if any, and releases the spinlock.

## State And Persistence
Persistent state per mutex includes the wait list, spinlock, `Cell<bool>` lock flag, and `UnsafeCell<T>` data. Wait entries are stack-local and unlink through `ListHead` drop. Thread parking state exists only under the `std` feature.

## Dependencies And Integration Points
It depends on `linked_list.rs`, `pin_init` macros, atomics, `UnsafeCell`, `Cell`, and optional `std::thread` primitives. The example is reused by other examples such as `static_init.rs`.

## Risks And Edge Cases
This is demonstrative code, not a production mutex. The spinlock busy-waits, `Cell<bool>` is protected only by the spinlock discipline, and wait-list manipulation relies on correct pinning and drop order. Without `std`, waiting does not actually block. Waking only one waiter and scheduling races around park/unpark are simplified.

## Test Signals
The included `main` under `std` spawns 20 workers and checks a final counter value. Additional signals include contention with many waiters, Miri with reduced workload, drop of waiting entries, `get_data_mut()` exclusive access, and sanitizer checks for intrusive-list pointer safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/mutex.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/pthread_mutex.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/pthread_mutex.rs

## Purpose
This example wraps a `libc::pthread_mutex_t` in a pinned Rust type initialized in place. It demonstrates fallible FFI initialization, pinned destruction, and shared ownership through `Arc::try_pin_init`.

## Important APIs, Types, And Functions
Inside `pthread_mtx`, `PThreadMutex<T>` is `#[pin_data(PinnedDrop)]` with pinned raw mutex storage, data, and `PhantomPinned`. `PThreadMutex::new(data)` returns `impl PinInit<Self, Error>`. `lock()` returns `PThreadMutexGuard<'_, T>`, which unlocks on drop and dereferences to `T`. The local `Error` enum represents OS and allocation failures.

## Control Flow
`new()` builds an initializer that initializes pthread attributes, sets the mutex type to `PTHREAD_MUTEX_NORMAL`, writes `PTHREAD_MUTEX_INITIALIZER`, calls `pthread_mutex_init`, destroys attributes, and returns an error on any failed libc call. Pinned drop calls `pthread_mutex_destroy`. The example `main()` creates a pinned `Arc`, spawns worker threads, increments the protected counter, joins all workers, and asserts the final value.

## State And Persistence
State is per `PThreadMutex`: raw pthread mutex bytes and `UnsafeCell<T>`. The mutex persists while the pinned owner exists and is destroyed in `PinnedDrop`. Thread-local work state is temporary.

## Dependencies And Integration Points
It depends on `libc`, `pin_init`, `std::thread`, `Arc`, and `core::pin::Pin`. It is disabled on Windows and ignored under Miri for the heavy pthread workload.

## Risks And Edge Cases
FFI safety depends on correct raw pointer casts through `UnsafeCell` and always destroying initialized pthread attributes. Return codes from `pthread_mutex_lock` and unlock are ignored. Destroying a locked pthread mutex would be erroneous, so users must not drop while guards exist. The large workload may be expensive in CI.

## Test Signals
Signals include successful concurrent counter increments, failure injection for pthread attribute and init calls, correct drop/destroy behavior, Windows cfg exclusion, Miri ignore behavior, and checking no raw mutex is moved after pinning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/pthread_mutex.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/static_init.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/examples/static_init.rs

## Purpose
`static_init.rs` demonstrates lazy one-time initialization of a static pinned value using `UnsafeCell<MaybeUninit<T>>`, a stored initializer, a spinlock, and a present flag.

## Important APIs, Types, And Functions
`StaticInit<T, I>` stores the cell, optional initializer, `SpinLock`, and `present` flag. `StaticInit::new(init)` is const. Its `Deref` implementation performs lazy initialization. `CountInit` implements `PinInit<CMutex<usize>>` and initializes a mutex after a delay. `COUNT` is a static `StaticInit<CMutex<usize>, CountInit>`.

## Control Flow
Dereferencing first checks `present`. If false, it takes the spinlock, rechecks `present`, takes the initializer out of the `Cell<Option<I>>`, calls `__pinned_init` on the static memory slot, marks `present = true`, and returns a shared reference. The example main concurrently updates both `COUNT` and a separate `Arc<CMutex<_>>`.

## State And Persistence
The static cell persists for the program lifetime. Once initialized, the value is never dropped. The initializer is consumed exactly once and `present` guards subsequent dereferences.

## Dependencies And Integration Points
It depends on the example mutex, `pin_init`, `UnsafeCell`, `MaybeUninit`, and optional `std` threading. It models how pinned static initialization might work in systems code.

## Risks And Edge Cases
The implementation is demonstrative and uses `Cell` in a static type with unsafe `Sync`; correctness depends on the spinlock protecting all mutation. It uses sleeps for demonstration, unwraps an infallible initializer, and calls `unreachable_unchecked` if the initializer is missing while `present` is false. The static value is leaked by design.

## Test Signals
Signals include multi-threaded first access racing through the spinlock, exactly-once initialization, final counter checks, no double initialization, and sanitizer/Miri review of unsafe `Sync` and `UnsafeCell` access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/examples/static_init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/diagnostics.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/diagnostics.rs

## Purpose
This file provides a small diagnostics accumulator for the `pin-init-internal` proc-macro crate. It lets macro expansion collect one or more `syn::Error` compile errors before returning a token stream.

## Important APIs, Types, And Functions
`DiagCtxt(TokenStream)` stores accumulated compile-error tokens. `ErrorGuaranteed` is an unconstructable marker returned after recording an error. `DiagCtxt::error(span, msg)` appends a `syn::Error::into_compile_error()`. `DiagCtxt::with(fun)` runs a macro expansion closure and combines generated output with accumulated diagnostics, or returns only diagnostics on fatal error.

## Control Flow
Macro entry points call `DiagCtxt::with`. Helper code reports recoverable errors into the context and may return `Err(ErrorGuaranteed)` for fatal expansion. On success, accumulated compile errors are appended to the normal stream; on fatal error, only diagnostics are emitted.

## State And Persistence
State is transient per macro invocation. There is no global diagnostic state.

## Dependencies And Integration Points
It depends on `proc_macro2::TokenStream`, `syn::Error`, and `Spanned`. All internal macro modules use it for consistent compile-error emission.

## Risks And Edge Cases
Appending errors to otherwise generated output can produce multiple diagnostics but may also trigger follow-on type errors if the partial expansion is not robust. Fatal errors must be returned when continuing would emit invalid code.

## Test Signals
Trybuild tests should validate multiple diagnostics from one macro invocation, fatal-only diagnostics, span placement, and absence of proc-macro panics for user errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/diagnostics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/init.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/init.rs

## Purpose
`init.rs` implements the `init!` and `pin_init!` procedural macros. It parses struct-initializer-like syntax and emits closure-based `Init` or `PinInit` objects that initialize fields in place, enforce field coverage/alignment at compile time, and clean up partially initialized fields on error.

## Important APIs, Types, And Functions
`Initializer` is the parsed macro input, with optional attributes, optional `&this in`, target path, fields, optional `..Zeroable::init_zeroed()`, and optional `? ErrorType`. `InitializerField` supports value fields (`field: expr` or shorthand), in-place fields (`field <- init`), and code blocks (`_: { ... }`). `expand(...)` is the generator. `get_init_kind`, `init_fields`, and `make_field_check` implement zeroing detection, field writes/drop guards, and compile-time checks.

## Control Flow
Expansion selects pinned or unpinned data traits, resolves the error type from explicit `?`, `#[default_error(...)]`, or a default. It obtains field metadata through `HasPinData` or `HasInitData`, optionally zeroes the whole slot if the rest expression is exactly `Zeroable::init_zeroed()`, creates a `this` `NonNull` if requested, emits initialization statements for each field, creates `DropGuard`s after each initialized field, exposes local references for later field initializers, performs unreachable compile-time field/alignment checks, forgets guards on success, and returns a closure converted through `pin_init_from_closure` or `init_from_closure`.

## State And Persistence
Generated initializers are one-shot closures. During initialization, state consists of the destination slot, per-field drop guards, local field bindings, and optional zeroed memory. If a later field initializer returns `Err` or panics after earlier fields initialized, active guards drop those fields; on success guards are forgotten and ownership transfers to the fully initialized object.

## Dependencies And Integration Points
It depends on `pin-init` runtime traits and internal tokens: `HasPinData`, `PinData`, `HasInitData`, `InitData`, `DropGuard`, `InitOk`, `Zeroable`, and initializer constructors. It is invoked by `pin-init/internal/src/lib.rs` for both `init` and `pin_init`.

## Risks And Edge Cases
The macro's safety hinges on never creating references to uninitialized or unaligned data. `make_field_check` uses unreachable code to let the compiler catch missing/duplicate fields and unaligned field references. Only the exact rest syntax `..Zeroable::init_zeroed()` is accepted. Cfg attributes on fields are preserved for initialization and guard forgetting. The `InitOk` token prevents user code from returning success without passing through macro-generated field checks.

## Test Signals
Trybuild coverage should include successful value and in-place fields, missing and duplicate fields, unaligned packed fields, zeroing trailer, custom error types, `&this in` self-references, cfg-gated fields, failure cleanup order, and pinned-field type enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/lib.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/lib.rs

## Purpose
This is the proc-macro crate entry point for `pin-init-internal`. It exposes macros used by the public `pin-init` crate: field pinning metadata, pinned drop transformation, zeroable derives, and initializer construction.

## Important APIs, Types, And Functions
Proc-macro exports are `#[pin_data]`, `#[pinned_drop]`, `#[derive(Zeroable)]`, `#[derive(MaybeZeroable)]`, `init!`, and `pin_init!`. The file wires each entry point to `pin_data`, `pinned_drop`, `zeroable`, or `init` helper modules through `DiagCtxt::with`.

## Control Flow
Each macro parses input with `syn::parse_macro_input!`, creates a diagnostic context, delegates to the corresponding expansion function, and converts the result back to `proc_macro::TokenStream`. `init!` and `pin_init!` both default the error type to `core::convert::Infallible` and differ by the `pinned` flag passed to `init::expand`.

## State And Persistence
No runtime state is held by this crate entry point. Generated output can define helper types, impls, and initializer closures in the caller crate.

## Dependencies And Integration Points
It depends on Rust proc-macro APIs, `syn`, and local modules. The public `pin-init/src/lib.rs` re-exports these proc macros under the user-facing crate.

## Risks And Edge Cases
The entry point must keep public macro names and defaults synchronized with `pin-init` documentation. Parse failures from `parse_macro_input!` short-circuit before custom diagnostics. Feature gates and fixdep version-string comments are part of the kernel build integration.

## Test Signals
Signals include expansion tests for all exported macros, parse-error diagnostics, default error type behavior, and public re-export compatibility from the main `pin-init` crate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pin_data.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pin_data.rs

## Purpose
`pin_data.rs` implements the `#[pin_data]` attribute. It marks structurally pinned fields, generates projection types and pin-data metadata used by `pin_init!`, controls `Unpin` derivation, and enforces pinned-drop discipline.

## Important APIs, Types, And Functions
`Args` parses optional `PinnedDrop`. `pin_data(args, input, dcx)` is the main expansion. Helpers include `is_phantom_pinned`, `generate_unpin_impl`, `generate_drop_impl`, `generate_projections`, `generate_the_pin_data`, `SelfReplacer`, and `collect_tuple`. Generated artifacts include `<Struct>Projection`, `project()`, `__ThePinData`, `HasPinData` and `PinData` impls, field initializer/projection functions, and drop/Unpin guard impls.

## Control Flow
The macro accepts structs only. It replaces `Self` in generics and fields with the concrete struct path, strips `#[pin]` field attributes while recording which fields were pinned, warns when a `PhantomPinned` field lacks `#[pin]`, then emits the original struct plus helper items inside a private const. For `Unpin`, it creates an internal `__Unpin` type containing only pinned fields and implements `Unpin` for the original type when that helper is `Unpin`. For drop, it either delegates `Drop` to `PinnedDrop` or creates conflicting traits that prevent normal `Drop` or forgotten `PinnedDrop` declarations.

## State And Persistence
Generated metadata is compile-time type state. At runtime, projection methods create `Pin<&mut Field>` for pinned fields and `&mut Field` for unpinned fields. The generated drop impl is persistent code for the type when `PinnedDrop` is requested.

## Dependencies And Integration Points
It depends on `syn` parsing/visiting, `quote`, `DiagCtxt`, and public `pin_init` traits. The initializer macro uses generated `__ThePinData` methods to ensure pinned fields receive `PinInit` and unpinned fields receive `Init`.

## Risks And Edge Cases
Only named-field structs are supported by generated projection code. `SelfReplacer` must avoid descending into nested items where `Self` changes meaning. Drop-prevention uses trait conflicts, so diagnostics may be compiler-generated but intentional. Forgetting `PinnedDrop` in the attribute or adding `Drop` directly is rejected by design. Unsafe projection correctness depends on the structurally pinned field list matching the user's `#[pin]` attributes.

## Test Signals
Trybuild tests should cover pinned and unpinned fields, generic bounds containing `Self`, tuple/enum/union rejection, `PhantomPinned` warnings/errors, `Unpin` behavior, projection types, direct `Drop` rejection, `PinnedDrop` delegation, and initializer enforcement for pinned fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pin_data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pinned_drop.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pinned_drop.rs

## Purpose
`pinned_drop.rs` implements the `#[pinned_drop]` attribute that turns a safe-looking `impl PinnedDrop for T` into the required unsafe trait implementation and adds the hidden token parameter that prevents manual calls.

## Important APIs, Types, And Functions
`pinned_drop(args: Nothing, input: ItemImpl, dcx)` validates and rewrites the impl. It uses `OnlyCallFromDrop` as the extra parameter type and rewrites the trait path to `::pin_init::PinnedDrop`.

## Control Flow
The macro rejects explicit `unsafe impl` because using the attribute is the safe implementation path, then marks the impl as unsafe internally. It validates that the impl targets `PinnedDrop` with the expected path and rejects negative or inherent impls. For the `drop` method, it appends an unused `OnlyCallFromDrop` argument to match the actual trait signature.

## State And Persistence
No runtime state is held. The generated impl becomes the type's pinned destructor implementation and is invoked from the `Drop` glue generated by `#[pin_data(PinnedDrop)]`.

## Dependencies And Integration Points
It depends on `syn`, `quote`, and `DiagCtxt`. It must stay synchronized with the public `PinnedDrop` trait in `pin-init/src/lib.rs` and the drop delegation emitted by `pin_data.rs`.

## Risks And Edge Cases
Path validation is strict and can reject unusual imports. If a user writes methods besides `drop`, they are preserved. The safety model depends on `OnlyCallFromDrop` remaining unconstructable by safe code and on `pin_data` being used with the `PinnedDrop` argument.

## Test Signals
Tests should include valid pinned drop impls, accidental `unsafe impl`, inherent impl rejection, negative impl rejection, wrong trait path diagnostics, missing `PinnedDrop` in `#[pin_data]`, and generated method signature compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pinned_drop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/zeroable.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/zeroable.rs

## Purpose
`zeroable.rs` implements derives for the public `Zeroable` marker trait. It supports strict deriving when all fields must implement `Zeroable` and a maybe-derive mode that silently fails when field bounds are not met.

## Important APIs, Types, And Functions
`derive(input, dcx)` handles `#[derive(Zeroable)]`. `maybe_derive(input, dcx)` handles `#[derive(MaybeZeroable)]`. Both accept structs and unions and reject enums. The generated unsafe impl targets `::pin_init::Zeroable`.

## Control Flow
For strict derive, the macro adds `Zeroable` bounds to type parameters, emits an unsafe impl, and emits a const helper that calls `assert_zeroable::<FieldType>()` for each field to force field validation. For maybe derive, it adds type-parameter and per-field HRTB `Zeroable` where predicates, then emits the unsafe impl; if the predicates are unsatisfied, normal trait selection prevents use rather than producing a custom derive error.

## State And Persistence
The only persistent effect is a trait implementation. No runtime state is generated.

## Dependencies And Integration Points
It depends on `syn`, `quote`, `DiagCtxt`, and the public `Zeroable` trait. The `init!` macro's zeroing trailer and `init_zeroed()` rely on correct `Zeroable` implementations.

## Risks And Edge Cases
Unsafe impl correctness rests on every field accepting the all-zero bit pattern and padding being safe to zero. Enums are rejected because not all discriminant values are valid. Maybe-derive's silent behavior can surprise users if they expect an impl but a field is not zeroable.

## Test Signals
Tests should include structs, unions, generic fields, non-zeroable fields, enums, maybe-derive success/failure, arrays/tuples, and use with `Zeroable::init_zeroed()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/internal/src/zeroable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/__internal.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/src/__internal.rs

## Purpose
`__internal.rs` contains runtime support items used by `pin-init` macros but hidden from normal users: closure initializer wrappers, pin/init data traits, stack initialization storage, drop guards for partially initialized fields, and tokens used to restrict unsafe internal calls.

## Important APIs, Types, And Functions
Key items are `Invariant<T>`, `InitClosure<F, T, E>`, `InitOk`, `HasPinData`, `PinData`, `HasInitData`, `InitData`, `AllData<T>`, `StackInit<T>`, `DropGuard<T>`, `OnlyCallFromDrop`, and `AlwaysFail<T>`. `StackInit::init` initializes stack storage and returns `Pin<&mut T>`.

## Control Flow
`InitClosure` delegates `Init` and `PinInit` calls to its stored closure. `StackInit::init` drops any previously initialized value before reusing the slot, runs the supplied pinned initializer, marks the slot initialized, and returns a pinned mutable reference. `DropGuard` drops its pointer on scope exit unless forgotten. `OnlyCallFromDrop` and `InitOk` are unsafe construction tokens used by generated code.

## State And Persistence
`StackInit` stores `MaybeUninit<T>` plus an `is_init` flag and drops initialized contents in its `Drop`. `DropGuard` owns a raw initialized pointer until forgotten. Other types are zero-sized or marker state for type inference and macro discipline.

## Dependencies And Integration Points
It depends on public `Init`, `PinInit`, `PinnedDrop`, `MaybeUninit`, `Pin`, and pointer APIs. Proc macros in `pin-init-internal` generate calls into these internals, especially field drop guards and data-trait lookups.

## Risks And Edge Cases
These APIs are hidden because their safety contracts are subtle. `StackInit::init` can drop a previously pinned value before reinitialization; it must never expose `&mut T` that would allow moves. `DropGuard` requires a valid, initialized, aligned pointer. `OnlyCallFromDrop` and `InitOk` rely on unsafe constructors not being misused outside generated code.

## Test Signals
Signals include the included `stack_init_reuse` test, failure cleanup with `DropGuard`, stack initialization and reinitialization, `AlwaysFail` with `assert_pinned!`, and compile tests that hidden traits are implemented only by generated code where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/__internal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/alloc.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/src/alloc.rs

## Purpose
`alloc.rs` adds allocation-backed in-place initialization support for `Box` and `Arc` when `std` or `alloc` is available. It lets users allocate uninitialized storage and initialize it with `Init` or `PinInit` without intermediate moves.

## Important APIs, Types, And Functions
`InPlaceInit<T>` provides `try_pin_init`, `pin_init`, `try_init`, and `init`. Implementations cover `Box<T>` and `Arc<T>`. `InPlaceWrite<T>` is implemented for `Box<MaybeUninit<T>>`. The file also marks `Box<T>` as `ZeroableOption`.

## Control Flow
`Box` initialization allocates `Box::try_new_uninit()` or `Box::new_uninit()` depending on features and delegates to `write_init` or `write_pin_init`. `Arc` initialization allocates an uninitialized `Arc`, gets the unique mutable slot with `Arc::get_mut`, runs the initializer, and then assumes initialization, pinning for the pinned path. Convenience methods convert infallible initializer errors into allocation-error results.

## State And Persistence
State is the allocated uninitialized storage and, after success, an initialized `Box<T>`, `Pin<Box<T>>`, `Arc<T>`, or `Pin<Arc<T>>`. On initializer error, allocation is deallocated without dropping uninitialized `T`.

## Dependencies And Integration Points
It depends on `alloc` or `std`, `AllocError`, `MaybeUninit`, `Pin`, `Init`, `PinInit`, `InPlaceWrite`, and initializer closure constructors. The public crate re-exports `InPlaceInit` for examples and users.

## Risks And Edge Cases
`Arc::get_mut` should always succeed immediately after allocation; the code treats failure as unreachable. Safety depends on not dropping uninitialized memory on failure and not moving a pinned allocation after initialization. Feature combinations change allocation APIs and error types.

## Test Signals
Tests should cover Box and Arc init/pin-init success, allocation failure conversion, initializer failure cleanup, `Box<MaybeUninit<T>>::write_*`, feature combinations with `std` and `alloc`, and `!Unpin` values remaining pinned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/alloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/lib.rs -->
# sources/distributed-fs/ceph-client/rust/pin-init/src/lib.rs

## Purpose
`lib.rs` is the public `pin-init` crate. It provides safe and fallible in-place initialization for pinned and unpinned values, stack and allocation targets, array helpers, scoped initializer construction, pinned destruction, zeroable initialization, and wrapper adapters.

## Important APIs, Types, And Functions
Public macros and re-exports include `pin_data`, `pinned_drop`, `Zeroable`, `MaybeZeroable`, `stack_pin_init!`, `stack_try_pin_init!`, `pin_init!`, `init!`, and `assert_pinned!`. Core traits are unsafe `PinInit<T, E>`, unsafe `Init<T, E>`, `InPlaceWrite<T>`, unsafe `PinnedDrop`, unsafe `Zeroable`, unsafe `ZeroableOption`, and `Wrapper<T>`. Important helpers include `pin_init_from_closure`, `init_from_closure`, `cast_pin_init`, `cast_init`, `uninit`, `init_array_from_fn`, `pin_init_array_from_fn`, `pin_init_scope`, `init_scope`, `init_zeroed`, and `zeroed`.

## Control Flow
Stack macros allocate a pinned `StackInit<T>` slot and run an initializer, either panicking on impossible `Infallible` errors or returning/propagating fallible results. `PinInit` and `Init` support chaining with `chain`, and blanket impls let plain `T` and `Result<T, E>` initialize slots by writing values. Array helpers initialize elements one at a time and drop already initialized elements on failure. Scope helpers run a pre-initialization closure and then run the returned initializer. Zeroing helpers write zero bytes only for `T: Zeroable`.

## State And Persistence
The crate itself has no global mutable state. Initializers are values/closures that consume themselves when run against a destination slot. `StackInit` and allocation integrations own storage until successful initialization. Zeroable trait impls and wrapper impls are persistent type-level contracts.

## Dependencies And Integration Points
It is `no_std` without the `std` feature, optionally uses `alloc`, and imports internal proc macros from `pin_init_internal`. It is used by Rust-for-Linux kernel abstractions and by the examples in this subset. `alloc.rs` provides Box/Arc support when enabled.

## Risks And Edge Cases
The central risk is unsafe initializer correctness: returning `Ok` must mean the slot contains a valid initialized value, while returning `Err` must leave no initialized owned value behind unless cleaned up. `cast_*` and `Wrapper` require layout compatibility. Zeroable implementations must be sound for all-zero bit patterns and must not include uninhabited types. Stack pinning must not allow moving pinned values. Feature gates (`allocator_api`, `unsafe-pinned`, `new_uninit`) affect portability.

## Test Signals
High-value tests include trybuild coverage for macro syntax and compile failures, runtime drop-order tests for partial initialization, array failure cleanup, stack initialization and reuse, Box/Arc in-place initialization, pinned-drop invocation, zeroed initialization for supported types, wrapper layout adapters, and no-std/std/alloc feature matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/pin-init/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/detection.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/detection.rs

## Purpose
`detection.rs` determines whether the compiler's real `proc_macro` API is available in the current context. `proc-macro2` uses this to choose between compiler-backed and fallback token implementations.

## Important APIs, Types, And Functions
`inside_proc_macro() -> bool` is the main query. `force_fallback()` stores a forced-fallback state. `unforce_fallback()` reruns detection. `WORKS: AtomicUsize` stores unknown/false/true as `0/1/2`, and `INIT: Once` ensures detection happens once in normal operation. `initialize()` has two cfg variants.

## Control Flow
`inside_proc_macro` first reads `WORKS`; if unknown, it calls `INIT.call_once(initialize)` and recurses. With modern `proc_macro::is_available()`, initialization stores availability plus one. On older compilers, initialization temporarily installs a null panic hook, calls `proc_macro::Span::call_site` inside `catch_unwind`, stores success/failure, restores the hook, and panics if another thread disturbed the hook sequence.

## State And Persistence
Detection result is process-global atomic state. `Once` prevents repeated normal detection; `force_fallback` can override the state to false, and `unforce_fallback` attempts to refresh it.

## Dependencies And Integration Points
It depends on `proc_macro`, `std::sync::Once`, atomics, and optionally `std::panic`. `fallback.rs::force` and `unforce` call these functions under `wrap_proc_macro`.

## Risks And Edge Cases
The old panic-hook probing path has a known race window where another thread's panic hook can be missed, and it detects hook tampering with a panic. `unforce_fallback()` calls `initialize()` directly rather than resetting `Once`. Relaxed atomics are enough for a cached availability flag but should not be used for richer state.

## Test Signals
Signals include behavior inside and outside proc macro contexts, forced fallback and unforce transitions, old-compiler cfg path with panic-hook restoration, multi-threaded first calls, and ensuring no spurious stderr panic output during detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/detection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/extra.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/extra.rs

## Purpose
`extra.rs` provides proc-macro2 APIs that do not directly correspond to stable `proc_macro` APIs. In this subset it exposes span invalidation for large parsing workloads and a compact delimiter-span wrapper.

## Important APIs, Types, And Functions
Under `span_locations`, `invalidate_current_thread_spans()` clears current-thread fallback span source maps. `DelimSpan` stores either compiler spans (`join`, `open`, `close`) or a fallback span. Methods `new`, `join`, `open`, and `close` return public `Span` wrappers. `Debug` formats the joined span.

## Control Flow
`DelimSpan::new` inspects an internal `imp::Group` and captures compiler open/close spans when wrapping real proc_macro groups; otherwise it stores a fallback group span. Accessors convert stored internal spans back into public `Span`, using first/last byte for fallback open/close spans.

## State And Persistence
`DelimSpan` is a small copyable value. Span invalidation mutates thread-local fallback state in `fallback.rs`; it does not affect other threads.

## Dependencies And Integration Points
It depends on internal `fallback`, `imp`, marker auto-trait machinery, and `Span`. The public API is useful to callers needing delimiter-level spans and to workloads parsing more than 4 GiB of source per thread.

## Risks And Edge Cases
Invalidating spans makes older spans on that thread invalid or incorrect, so callers must not keep using them. `invalidate_current_thread_spans()` panics or is unavailable in proc-macro contexts. Fallback open/close spans approximate delimiters with first/last bytes of the group span.

## Test Signals
Tests should cover compiler-backed and fallback `DelimSpan`, open/close/join values, debug formatting, span invalidation after large parse simulations, and panic behavior when invalidation is called from an unsupported context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/extra.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/fallback.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/fallback.rs

## Purpose
`fallback.rs` implements proc-macro2's compiler-independent token model. It provides fallback `TokenStream`, `Group`, `Ident`, `Literal`, `Span`, parsing/printing, source-location support, and conversions used when real `proc_macro` is unavailable or forced off.

## Important APIs, Types, And Functions
Top-level controls are `force()` and `unforce()`. Core types are `TokenStream`, `LexError`, `TokenStreamBuilder`, `Span`, `Group`, `Ident`, and `Literal`. Source-location support includes thread-local `SOURCE_MAP`, `FileInfo`, `SourceMap`, `lines_offsets`, and `invalidate_current_thread_spans`. Utility functions include `get_cursor`, `push_token_from_proc_macro`, identifier validators, `escape_utf8`, and feature-gated `FromStr2` for panic-safe compiler parsing.

## Control Flow
`TokenStream::from_str_checked` creates a parser cursor, strips a byte-order mark, and delegates token parsing. Token streams use reference-counted vectors and builders; extending a stream normalizes negative literals into `-` plus a positive literal token. `Display` prints tokens with spacing controlled by punct jointness. `Drop` walks nested fallback groups iteratively to avoid recursive stack overflow. Span-location parsing registers each source string in a thread-local source map and assigns monotonically increasing 32-bit character offsets; span methods map offsets to line/column, byte ranges, file labels, source text, joins, and delimiter endpoints.

## State And Persistence
Fallback token streams persist token vectors and spans. Under `span_locations`, each thread keeps a source map of parsed strings until invalidated, with lazy char-index-to-byte-offset caches per file. `force()` and `unforce()` affect global proc-macro2 detection state through `detection.rs`.

## Dependencies And Integration Points
It depends on internal parser cursors, `RcVec`, public token enums, `Delimiter`, `Spacing`, optional `LineColumn`, `alloc::BTreeMap`, and optional real `proc_macro` parsing. It is the core fallback for all proc-macro2 users outside compiler proc-macro contexts.

## Risks And Edge Cases
Span offsets are 32-bit and can wrap for very large same-thread parse workloads; `extra::invalidate_current_thread_spans` is the mitigation. Source-map lookups assert that spans are valid and within one file. Identifier validation is ASCII-only here, so behavior differs from full Rust Unicode identifiers. `Literal::from_str_checked` handles negative literals specially and escapes NULs carefully to avoid octal ambiguity. Compiler conversion uses fallback validation first because rustc can panic on invalid token streams.

## Test Signals
High-value tests include parsing and displaying nested token streams, nonrecursive drop of deeply nested groups, negative literal normalization, span line/column/source-text lookup, source-map invalidation, identifier and raw identifier validation, literal constructors for strings/bytes/C strings/numbers, BOM stripping, invalid token errors, and compiler conversion panic handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/fallback.rs -->
