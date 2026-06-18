# subset-b-009680 research

Grouped research for vendored Boost.Unordered support headers and fmt headers used by mergerfs. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/mulx.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/mulx.hpp

## Purpose

This Boost.Unordered detail header provides a small multiplication-based bit mixer. It exposes `mulx64`, `mulx32`, and `mulx(std::size_t)` in `boost::unordered::detail`, selecting a 64-bit or 32-bit mixing path according to detected `std::size_t` width. The mixer is intended for hash-table internals where a hash value needs a cheap avalanche step based on the high and low halves of a product.

## Important APIs, types, and functions

`mulx64(boost::uint64_t, boost::uint64_t)` computes a full 128-bit product and returns low-half XOR high-half. It has platform-specific implementations for MSVC x64 (`_umul128`), MSVC ARM64 (`__umulh` plus the normal product), compilers with `__uint128_t`, and a portable 32-bit-limb fallback.

`mulx32(boost::uint32_t, boost::uint32_t)` multiplies to 64 bits and XORs the two 32-bit halves. Under `__MSVC_RUNTIME_CHECKS` it masks the low half before narrowing to avoid Visual Studio runtime narrowing diagnostics.

`mulx(std::size_t)` is the public convenience mixer. On detected 64-bit-or-larger architectures it calls `mulx64(x, 0x9E3779B97F4A7C15ull)`, the golden-ratio multiplier. On 32-bit architectures it calls `mulx32(x, 0xE817FB2Du)`, a multiplier cited from the referenced arXiv hashing paper.

## Control Flow

Most control flow is preprocessor-driven. The file first chooses the best `mulx64` implementation at compile time, then detects whether `SIZE_MAX` or `UINTPTR_MAX` implies a 64-bit `size_t`. `mulx` uses that temporary `BOOST_UNORDERED_64B_ARCHITECTURE` macro and undefines it before leaving the header.

The portable `mulx64` path splits both inputs into high and low 32-bit limbs, combines partial products, propagates carry from the middle limbs, and returns reconstructed low-half XOR high-half. There is no runtime branching outside the small 32-bit mask path selected for MSVC runtime checks.

## State and Persistence Behavior

The header is stateless. It defines only inline functions and temporary macros. No data is persisted, cached, allocated, or synchronized.

## Dependencies and Integration Points

It depends on Boost integer typedefs from `boost/cstdint.hpp`, C limits, and `<cstddef>`. On MSVC it includes `<intrin.h>`. The integration point is Boost.Unordered internals that need size-dependent hash mixing without depending on a heavier hashing component.

## Risks and Edge Cases

The architecture decision treats widths greater than 64 bits as 64-bit. That is intentional in the macro comment but would discard entropy above 64 bits if used on unusual platforms. The fallback arithmetic is subtle carry code; regressions would create platform-specific hash distribution differences. The MSVC intrinsic branches exclude clang-cl, so clang-cl relies on the `__uint128_t` or fallback path. The mixer is not cryptographic and should not be used as a security boundary.

## Test Signals

Useful tests compare `mulx64` fallback output against a known 128-bit implementation, verify `mulx32` against hand-computed products, and compile on MSVC x64/ARM64 plus GCC/Clang. Hash-table tests should look for stable behavior across 32-bit and 64-bit builds, reasonable bucket distribution, and absence of runtime-check narrowing failures on Visual Studio.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/mulx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/narrow_cast.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/narrow_cast.hpp

## Purpose

This header defines `boost::unordered::detail::narrow_cast`, a constrained integral narrowing helper for Boost.Unordered internals. It documents and enforces the assumption that a conversion intentionally drops high bits from an integral source whose type is at least as wide as the destination.

## Important APIs, types, and functions

`template<typename To, typename From> constexpr To narrow_cast(From x) noexcept` is the only API. It uses `BOOST_UNORDERED_STATIC_ASSERT` to require `From` and `To` to be integral and `sizeof(From) >= sizeof(To)`. The returned value is a `static_cast<To>`.

Under `__MSVC_RUNTIME_CHECKS`, the expression masks `x` with an unsigned all-ones mask for the target type before casting. This suppresses Visual Studio's runtime check for data loss when the narrowing is deliberate.

## Control Flow

The function has no runtime control flow in normal builds. Compile-time assertions reject invalid type combinations. In MSVC runtime-check builds, the return expression includes a target-width mask generated through `std::make_unsigned<To>`.

## State and Persistence Behavior

The header is stateless and inline-only. It does not allocate, cache, mutate globals, or persist any values.

## Dependencies and Integration Points

It depends on `boost/unordered/detail/static_assert.hpp`, `boost/config.hpp`, and `<type_traits>`. It is used by low-level unordered implementation code that needs explicit narrowing without repeating assertions or carrying platform-specific MSVC runtime-check workarounds.

## Risks and Edge Cases

The helper does not check at runtime that the source value fits in `To`; it explicitly permits truncation. Signed inputs and signed destinations follow C++ conversion rules after the optional mask, so callers must not mistake this for a safe numeric cast. The size assertion prevents widening but does not distinguish value range differences between same-size signed and unsigned types.

## Test Signals

Compile-time tests should verify rejection of non-integral types and source types smaller than the destination. Runtime tests should cover truncation from 64 to 32 bits, signed and unsigned inputs, and Visual Studio runtime-check builds where the helper should not trigger narrowing diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/narrow_cast.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/opt_storage.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/opt_storage.hpp

## Purpose

This Boost.Unordered detail header defines an uninitialized storage wrapper for optional-like object lifetime management. It gives implementation code a place to store a `T` without constructing or destroying it automatically.

## Important APIs, types, and functions

`template<class T> union opt_storage` contains one member, `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS T t_`. The default constructor and destructor are intentionally empty. `address()` and `address() const` return `std::addressof(t_)`, avoiding overloaded `operator&`.

## Control Flow

The type has no runtime branching. Its behavior is controlled by C++ union lifetime rules: construction, destruction, and assignment of the contained `T` are the responsibility of the owning optional-like structure.

## State and Persistence Behavior

`opt_storage` stores raw object storage only. It does not track whether `t_` is live. Any surrounding container must maintain engagement state and must explicitly construct and destroy `T` at `address()`.

## Dependencies and Integration Points

It includes `boost/config.hpp` for `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS` and `<memory>` for `std::addressof`. It integrates with Boost.Unordered internals that need compact optional storage for node buffers or metadata without pulling in `std::optional` or imposing automatic lifetime behavior.

## Risks and Edge Cases

The main risk is lifetime misuse. Reading `t_` before placement construction or failing to destroy a live non-trivial `T` is undefined behavior. The empty destructor makes leaks of non-trivial `T` invisible to the type system. `BOOST_ATTRIBUTE_NO_UNIQUE_ADDRESS` can affect layout and should be validated on supported compilers.

## Test Signals

Tests should exercise construction and destruction by the owning wrapper, especially for non-trivial types with counters. Layout-sensitive tests can check size reductions for empty types where the attribute is supported. Sanitizer runs are useful because misuse normally appears as lifetime or leak errors rather than local assertion failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/opt_storage.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/serialization_version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/serialization_version.hpp

## Purpose

This header provides `serialization_version<T>`, a Boost.Unordered helper that captures the serialized version of another type `T` from a Boost.Serialization archive. It exists because `boost::serialization::load_construct_adl` asks user code to pass a version even though the archive already stores that version.

## Important APIs, types, and functions

`template<typename T> struct serialization_version` stores an `unsigned int value`. Its default constructor initializes `value` to `boost::serialization::version<serialization_version>::value`, which is specialized later to match `version<T>::value`.

The type supports assignment from `unsigned int` and implicit conversion to `unsigned int`, so callers can pass it where a version number is needed. Its private Boost.Serialization hooks implement `serialize`, `save`, and `load`; `save` does nothing, while `load` receives the archive-provided version parameter and stores it.

The specialization `boost::serialization::version<boost::unordered::detail::serialization_version<T>>` forwards `value` to `version<T>::value`, making this wrapper serialize with the same version metadata as `T`.

## Control Flow

During saving, the wrapper contributes no archive data. During loading, Boost.Serialization dispatches through `serialize`, `core::split_member`, and `load`, passing the version read from the archive. `load` copies that version into the wrapper instance for later use by unordered loading code.

## State and Persistence Behavior

The wrapper stores only the captured version number. It does not persist a separate field in the archive; it piggybacks on Boost.Serialization version metadata. The state is short-lived and local to deserialization.

## Dependencies and Integration Points

It depends on `boost/config.hpp` and `boost/core/serialization.hpp`. It integrates with Boost.Serialization through friendship with `boost::serialization::access`, `core::split_member`, and the `boost::serialization::version` specialization.

## Risks and Edge Cases

Correctness depends on the archive actually invoking serialization for the wrapper so that the version parameter is delivered. If `T` has no explicit version specialization, the wrapper reports the default version. The implicit conversion is convenient but can hide accidental use after default construction rather than after archive loading.

## Test Signals

Serialization tests should save data with multiple historical `version<T>` values and verify loading captures the stored value. Compile tests should confirm the wrapper has the same Boost.Serialization version as `T`. Regression tests should cover construction paths that call `load_construct_adl`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/serialization_version.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/static_assert.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/static_assert.hpp

## Purpose

This very small header centralizes Boost.Unordered's static assertion macro. It wraps C++ `static_assert` so internal headers can use a consistent project macro name and message style.

## Important APIs, types, and functions

`BOOST_UNORDERED_STATIC_ASSERT(...)` expands to `static_assert(__VA_ARGS__, #__VA_ARGS__)`. The expression text becomes the assertion message. The header also includes `boost/config.hpp` and enables `#pragma once` when `BOOST_HAS_PRAGMA_ONCE` is defined.

## Control Flow

There is no runtime control flow. The macro affects compilation only; failing assertions reject the translation unit.

## State and Persistence Behavior

The header has no state. It defines one macro guarded by include guards.

## Dependencies and Integration Points

It is included by other Boost.Unordered detail headers such as `narrow_cast.hpp`. The integration point is compile-time contract enforcement for internal templates.

## Risks and Edge Cases

The macro always stringizes the full variadic expression as the message, so custom explanatory messages are not supported through this wrapper. It also requires language support for C++11 `static_assert`, which is consistent with the surrounding vendored Boost.Unordered code.

## Test Signals

Compile-fail tests should verify that invalid template instantiations using this macro fail with the stringized condition. Include-order tests should verify the macro is available and does not conflict with other Boost headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/static_assert.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/type_traits.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/type_traits.hpp

## Purpose

This header collects Boost.Unordered-specific type traits and compatibility aliases. It fills gaps across C++ standards and old standard libraries, supports transparent lookup constraints, and provides deduction-guide helper traits for unordered container constructors.

## Important APIs, types, and functions

General utilities include `type_identity`, `make_void`, `void_t`, `is_complete`, `is_complete_and_move_constructible`, `remove_cvref_t`, `is_similar`, `is_similar_to_any`, and a pre-C++17 `as_const` fallback.

Compatibility aliases provide `is_trivially_default_constructible`, `is_trivially_copy_constructible`, and `is_trivially_copy_assignable`, using old libstdc++ `std::has_trivial_*` traits when modern traits are unavailable.

`is_nothrow_swappable<T>` detects whether unqualified `swap(T&, T&)` is available and `noexcept`. The implementation uses ADL through `using std::swap`.

Transparent lookup helpers include `is_transparent<T>`, `are_transparent<Key, Hash, KeyEqual>`, and `transparent_non_iterable<Key, UnorderedMap>`. The latter ensures heterogeneous lookup is enabled only when both hash and equality are transparent and the key is not convertible to iterator types.

When `BOOST_UNORDERED_TEMPLATE_DEDUCTION_GUIDES` is enabled, deduction-guide helpers include `is_input_iterator_v`, `is_allocator_v`, `is_hash_v`, `is_pred_v`, `iter_key_t`, `iter_val_t`, and `iter_to_alloc_t`.

## Control Flow

All behavior is compile-time template selection. Preprocessor gates enable C++17 deduction-guide helpers when supported and select old libstdc++ fallbacks with `BOOST_WORKAROUND`. SFINAE through `void_t` controls trait specialization.

## State and Persistence Behavior

There is no runtime state. The file defines types, aliases, and constants consumed at compile time by container templates.

## Dependencies and Integration Points

The header depends on Boost.Config, Boost workaround macros, `<type_traits>`, `<utility>`, and `<iterator>` when deduction guides are supported. It is an integration point for Boost.Unordered container overload participation, heterogeneous lookup, allocator/hash/predicate disambiguation, swap exception specifications, and older compiler support.

## Risks and Edge Cases

Traits that inspect incomplete types must avoid instantiating standard traits on incomplete inputs; `is_complete_and_move_constructible` handles that with `std::conditional`. Transparent lookup constraints must avoid accepting iterator-like keys, or overloads can become ambiguous. Deduction guide heuristics intentionally approximate standard requirements, so unusual iterators, allocators, or hash-like integral types can expose edge cases. Old libstdc++ fallbacks rely on deprecated compiler traits.

## Test Signals

Compile tests should cover incomplete types, ADL swap with throwing and non-throwing overloads, transparent hash/equality with heterogeneous keys, iterator-convertible keys rejected from heterogeneous overloads, and deduction-guide construction from iterators and allocators. Cross-toolchain CI on old libstdc++, C++11/14/17/20 modes, and MSVC is particularly valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/type_traits.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/unordered_printers.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/unordered_printers.hpp

## Purpose

This generated header embeds Python GDB pretty-printers and xmethods for Boost.Unordered containers into ELF objects through the `.debug_gdb_scripts` section. When enabled, GDB can discover and display Boost unordered maps, sets, flat/open-addressing containers, concurrent containers, iterators, and stats objects without separate Python files.

## Important APIs, types, and functions

The C++ surface is only preprocessor guards plus an `__asm__` block. The embedded Python defines `BoostUnorderedHelpers`, `BoostUnorderedPointerCustomizationPoint`, `BoostUnorderedFcaPrinter`, `BoostUnorderedFcaIteratorPrinter`, `BoostUnorderedFoaPrinter`, `BoostUnorderedFoaIteratorPrinter`, stats printers, and `BoostUnorderedFoaGetStatsMethod`/matcher.

FCA printers traverse classic bucket chains through `table_`, `buckets_`, and node `next` pointers. FOA printers traverse flat/open-addressing arrays using group metadata, occupied masks, sentinel detection, and element pointers. Both map printers yield alternating key/value children; set printers yield index/value pairs.

The xmethod exposes `get_stats` for supported flat/node unordered and concurrent containers, returning `table_.cstats` when the binary was compiled with stats.

## Control Flow

The C++ preprocessor includes the embedded script only when `BOOST_ALL_NO_EMBEDDED_GDB_SCRIPTS` is not defined and the target is ELF. Clang diagnostics are suppressed around the long assembly string.

At debug time, GDB loads the inlined script, builds a `RegexpCollectionPrettyPrinter`, registers template regexes for Boost.Unordered types, and registers an xmethod matcher. Printer `children()` methods are generators that walk container internals until bucket counts, null nodes, occupied masks, or sentinels terminate traversal.

## State and Persistence Behavior

The header adds debug metadata to compiled objects but no runtime data or executable program behavior. In GDB, printer instances hold references to inspected values, table pointers, pointer customization helpers, and derived flags such as `is_map`. The xmethod prints a diagnostic if stats were not compiled in.

## Dependencies and Integration Points

It depends on ELF debug-script support and GDB Python modules `gdb.printing`, `gdb.xmethod`, `re`, and `math`. It is tightly coupled to Boost.Unordered internal layout names such as `table_`, `buckets_`, `arrays`, `groups_`, `elements_`, `size_ctrl`, `buf.t_`, and FOA group metadata. Fancy pointer support integrates with external pretty-printers that implement `boost_to_address` and `boost_next`.

## Risks and Edge Cases

The script is layout-sensitive. Any internal field rename or group representation change can break debugging while normal code still compiles. Optimized builds may omit some constants, so the FOA printer hardcodes `N = 15` and `sentinel_ = 1`. Fancy pointer support depends on optional methods in other printers. The embedded assembly is ELF-specific and disabled elsewhere, so debugger behavior differs by platform. Very large containers can be expensive to expand in GDB.

## Test Signals

Debug tests should compile small programs containing each supported container, load them in GDB, and verify summaries, children, iterator displays, and stats xmethod behavior. Tests should cover classic node containers, flat containers, concurrent containers, maps versus sets, empty and non-empty states, optimized builds, fancy pointer allocators, and builds with `BOOST_ALL_NO_EMBEDDED_GDB_SCRIPTS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/unordered_printers.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/unordered_flat_map_fwd.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/unordered/unordered_flat_map_fwd.hpp

## Purpose

This Boost.Unordered public forward header declares `boost::unordered::unordered_flat_map` and its non-member operations without including the full implementation. It reduces compile-time coupling for code that only needs declarations.

## Important APIs, types, and functions

The main declaration is `template<class Key, class T, class Hash = boost::hash<Key>, class KeyEqual = std::equal_to<Key>, class Allocator = std::allocator<std::pair<const Key, T>>> class unordered_flat_map;`.

It also declares `operator==`, `operator!=`, and non-member `swap`, with `swap` using `noexcept(noexcept(lhs.swap(rhs)))` to mirror the member swap's exception specification. When `<memory_resource>` is available, it defines `boost::unordered::pmr::unordered_flat_map` as an alias using `std::pmr::polymorphic_allocator<std::pair<const Key, T>>`.

Finally, it brings the type into namespace `boost` with `using boost::unordered::unordered_flat_map`.

## Control Flow

There is no runtime control flow. Preprocessor logic includes memory-resource support unless `BOOST_NO_CXX17_HDR_MEMORY_RESOURCE` is defined, and enables `#pragma once` through Boost.Config.

## State and Persistence Behavior

The file declares types and functions only. It creates no objects and owns no state. ABI and persistence concerns are deferred to the full unordered flat map implementation.

## Dependencies and Integration Points

It depends on Boost.Config, `boost/container_hash/hash_fwd.hpp`, `<functional>`, `<memory>`, and optionally `<memory_resource>`. It integrates with users that forward-declare or store pointers/references to `unordered_flat_map`, and with PMR-aware code that wants the standard polymorphic allocator spelling.

## Risks and Edge Cases

Default template arguments in forward declarations must remain synchronized with the full definition. The PMR alias depends on standard library support and is absent when memory-resource headers are disabled. Non-member declarations must match implementation signatures exactly to avoid ODR or overload issues.

## Test Signals

Compile tests should include this header alone, declare pointers/references, use the `boost::unordered_flat_map` using-declaration, and compile PMR aliases when the standard library supports them. Link tests should verify equality and swap declarations resolve when the full implementation is included elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/unordered/unordered_flat_map_fwd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/version.hpp

## Purpose

This Boost configuration header records the vendored Boost release version. It is the canonical Boost header expected to change on every Boost release and is used by client code and Boost auto-link logic.

## Important APIs, types, and functions

`BOOST_VERSION` is defined as `109000`, encoding major, minor, and patch as `major * 100000 + minor * 100 + patch`. That value corresponds to Boost 1.90.0.

`BOOST_LIB_VERSION` is defined as the string `"1_90"`, the form used by Boost auto-link configuration to select versioned library names.

## Control Flow

There is no runtime or compile-time branching beyond the include guard. The comments document how to decode the numeric macro.

## State and Persistence Behavior

The header defines version macros only. It stores no runtime state. Because many files may include it, changing it intentionally causes broad recompilation.

## Dependencies and Integration Points

It has no includes. It integrates with Boost.Config documentation, feature checks, build scripts, and auto-link selection via `config/auto_link.hpp` in environments that use Boost's library naming conventions.

## Risks and Edge Cases

The macros must match the actual vendored Boost tree. A mismatch can confuse conditional compilation, diagnostics, package reporting, or auto-link library selection. Since this repository vendors selected Boost headers, consumers may assume more Boost components at version 1.90 than are actually present.

## Test Signals

Build metadata checks should confirm `BOOST_VERSION == 109000` and `BOOST_LIB_VERSION == "1_90"` match the vendored source snapshot. Downstream compile tests can include this header alone and verify version-gated code paths select expected Boost 1.90 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/version.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/args.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/args.h

## Purpose

This fmt header implements dynamic formatting argument storage. It lets callers build a runtime list of positional and named arguments that can later be converted to `fmt::basic_format_args<Context>` for type-erased APIs such as `vformat`.

## Important APIs, types, and functions

`detail::is_reference_wrapper` and `detail::unwrap` detect and unwrap `std::reference_wrapper` so callers can intentionally store references for supported types.

`detail::dynamic_arg_list` is a linked list of polymorphic nodes. Each `typed_node<T>` owns a copied value and the list is used for values whose storage must not relocate because `basic_format_arg` entries point to them.

`template<typename Context> class dynamic_format_arg_store` owns `data_`, `named_info_`, and `dynamic_args_`. It exposes `push_back` overloads for ordinary values, `std::reference_wrapper`, and `fmt::arg` named arguments; `clear`; `reserve`; `size`; and implicit conversion to `basic_format_args<Context>`.

The `need_copy<T>` trait determines whether a value must be copied into stable dynamic storage. Strings and custom types are copied unless passed as references; built-in scalar types and string views can fit directly into `basic_format_arg`.

## Control Flow

`push_back` checks `need_copy<T>::value`. Values needing stable storage are copied into `dynamic_args_`, and the resulting reference is converted into a `basic_format_arg`. Values not needing a copy are unwrapped and emplaced directly.

Named arguments reserve slot zero in `data_` for a `named_arg_value` table. `emplace_arg(named_arg)` inserts that sentinel when the first named argument arrives, appends the actual value, pushes name/id metadata, and updates `data_[0]`. A small unique_ptr guard rolls back the appended value if `named_info_` insertion throws.

## State and Persistence Behavior

The store owns all copied argument state until `clear` or destruction. `data_` must remain contiguous because `basic_format_args` references it. `dynamic_args_` is a linked list specifically to avoid relocation invalidating references held by `data_`. Named argument names are copied into dynamic storage before their `const char_type*` is recorded.

## Dependencies and Integration Points

It includes `<functional>`, `<memory>`, `<vector>`, and fmt `format.h`. It depends on fmt internals such as `mapped_type_constant`, `basic_format_arg`, `named_arg_info`, `named_arg`, `std_string_view`, and `fmt::arg`. It is the dynamic counterpart to compile-time `make_format_args`.

## Risks and Edge Cases

Lifetime rules are central. Passing a reference wrapper stores a live reference, so the caller must keep the referenced object alive. Built-in types and string views are always copied or stored directly, and the reference-wrapper overload statically rejects cases where referencing would not make sense. Named argument index math accounts for the hidden sentinel; off-by-one regressions would break lookup. Exception safety around named metadata is handled for the value append, but allocation failures must still preserve vector invariants.

## Test Signals

Tests should cover positional values, custom types, strings, string views, reference wrappers observing later mutation, named arguments, duplicate names handled by lower layers, `reserve`, `clear`, and conversion to `basic_format_args`. Exception-injection tests around named argument insertion would validate rollback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/base.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/base.h

## Purpose

This fmt header is the base API for char/UTF-8 formatting. It defines version and portability macros, core type traits, string views, parse contexts, format-spec parsing, type-erased argument storage, output buffers, compile-time format string checking, default native formatter scaffolding, and public `format_to`, `formatted_size`, `print`, and `println` entry points.

## Important APIs, types, and functions

Public surface includes `FMT_VERSION 120100`, `fmt::basic_string_view`, `fmt::string_view`, `fmt::parse_context`, `fmt::locale_ref`, `fmt::formatter`, `fmt::format_context`, `fmt::format_args`, `fmt::basic_format_arg`, `fmt::basic_format_args`, `fmt::basic_appender`, `fmt::format_string`, `fmt::runtime`, `fmt::make_format_args`, `fmt::arg`, `fmt::vformat_to`, `fmt::format_to`, `fmt::format_to_n`, `fmt::formatted_size`, `fmt::print`, and `fmt::println`.

Important internal types include `basic_specs`, `format_specs`, `dynamic_format_specs`, `type_mapper`, `value<Context>`, `format_arg_store`, `named_arg_store`, `native_formatter`, `buffer`, `iterator_buffer`, `container_buffer`, `counting_buffer`, `compile_parse_context`, and `format_string_checker`.

## Control Flow

The top of the file configures compiler, standard library, constexpr, consteval, exception, visibility, inlining, namespace, Unicode, and ABI-related macros. Runtime formatting flow starts with a public API building a `vargs`/`format_arg_store`, converting it to `format_args`, and dispatching to `detail::vformat_to` or print functions declared here and defined in `format.h`/the fmt library.

Format-string parsing is a scanner over text and replacement fields. `parse_format_string` walks literal text, handles escaped braces, and delegates replacement fields to `parse_replacement_field`. Argument IDs are parsed by `parse_arg_id`, with `parse_context` enforcing that automatic and manual indexing are not mixed. `parse_format_specs` implements alignment, fill, sign, alternate form, zero padding, width, precision, locale, and presentation type validation against the mapped argument type.

Compile-time checking uses `fstring`, `format_string_checker`, `compile_parse_context`, and per-argument formatter `parse` functions when consteval support is available. Runtime strings can opt out through `fmt::runtime`.

## State and Persistence Behavior

Most state is per-call and stack/local: parse contexts hold the remaining format-string view and next argument index; `basic_format_args` is a view over a store; `context` holds output iterator, argument view, and locale reference. Buffers own or reference output storage and flush through destructors or `out()` calls. `basic_format_args` does not own arguments, so storing it beyond the originating call can leave dangling references.

`basic_specs` packs format options into an integer plus a small fill buffer. `value<Context>` is a tagged union for built-in values, strings, pointers, custom format handles, and named argument tables. Custom values keep a raw pointer plus a function pointer to instantiate the relevant formatter.

## Dependencies and Integration Points

The header uses minimal C/C++ headers when not in module mode: limits, stdio, string functions, and type traits. It integrates with fmt `format.h` for definitions of declared formatting functions, native formatter `format` bodies, memory buffers, numeric writers, and platform-specific printing. It also integrates with user `formatter<T>` specializations, `format_as`, named arguments, locale-aware formatting, and Windows mojibake handling.

## Risks and Edge Cases

This is central infrastructure, so ABI and lifetime mistakes have wide blast radius. `basic_format_args` is a non-owning view. Mixing character types is statically rejected. Arbitrary non-void pointers are intentionally disallowed. Dynamic width and precision must resolve to integral arguments. Fill parsing handles multi-code-unit code points and rejects `{` as fill. Compile-time checking depends on compiler consteval support and has fallbacks for older compilers. Output iterator buffering must flush correctly on destruction while avoiding exceptions during unwinding.

## Test Signals

Strong signals include fmt's compile-time and runtime format-string tests, invalid specifier diagnostics, automatic/manual indexing errors, dynamic width and precision validation, named argument lookup, custom formatter dispatch, non-void pointer rejection, Unicode and non-UTF-8 Windows print paths, truncation reporting for fixed arrays, output iterator correctness, locale formatting, and cross-compiler builds with exceptions disabled and old language modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/chrono.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/chrono.h

## Purpose

This fmt header adds formatting support for C and C++ chrono/time types. It covers safe duration conversion, `std::tm`, `std::chrono::duration`, system/UTC/local time points, and C++20 calendar types or local fallbacks.

## Important APIs, types, and functions

Public aliases include `fmt::sys_time`, `fmt::utc_time`, and `fmt::local_time`. `fmt::gmtime` converts `time_t` or `sys_time` to UTC `std::tm` using thread-safe platform functions when possible.

Formatter specializations cover `std::chrono::duration<Rep, Period>`, `std::tm`, `sys_time<Duration>`, `utc_time<Duration>`, `local_time<Duration>`, and calendar types `weekday`, `day`, `month`, `year`, and `year_month_day`.

Internal machinery includes `safe_duration_cast` helpers, `detail::duration_cast`, `parse_chrono_format`, `tm_format_checker`, `chrono_format_checker`, `tm_writer`, `duration_formatter`, `get_locale`, fractional-second helpers, unit-name mapping through `get_units`, and locale transcoding helpers for time strings.

## Control Flow

Duration conversion routes through checked integral and floating conversions when `FMT_SAFE_DURATION_CAST` is enabled. Overflow or unsupported range throws `format_error("cannot format duration")`.

Chrono format parsing requires `%`-style specifiers. `parse_chrono_format` scans text, handles padding modifiers `_` and `-`, dispatches date/time/duration/timezone callbacks, supports `E` and `O` alternative forms, and rejects unsupported specifiers. Checkers validate whether a format is legal for `std::tm` or a duration before formatting.

`tm_writer` formats calendar fields from a `std::tm`. It uses fast classic-locale paths for common fields and delegates to `std::time_put` when localized output is needed. `duration_formatter` maps a duration to days/hours/minutes/seconds/subseconds, handles negative values and NaN/Inf for floating reps, and supports `%Q` for value and `%q` for units.

Time-point formatters convert to `std::tm` using UTC conversion for `sys_time`, `utc_clock::to_sys` for `utc_time`, and a no-timezone `gmtime` interpretation for `local_time`. Subsecond adjustment handles negative fractional epochs.

## State and Persistence Behavior

Formatter instances retain parsed specs, dynamic width/precision references, locale flags, and the chrono format substring. Per-format calls allocate temporary memory buffers before applying outer width/alignment. `get_locale` conditionally placement-constructs a `std::locale` in a union and destroys it manually. No global mutable state is used except static classic locale and UTC string storage.

## Dependencies and Integration Points

It depends on `<chrono>`, `<ctime>`, `<locale>`, streams, math, algorithms, and fmt `format.h`. It integrates with standard C time APIs (`gmtime_r`, `gmtime_s`, `std::gmtime`), `std::time_put`, codecvt-based localized string conversion, C++20 chrono calendar/time-zone types when present, and fmt's base parser, buffers, locale references, and numeric writers.

## Risks and Edge Cases

Duration casts can overflow; safe mode reduces undefined behavior but mixed integer/floating casts still fall back to standard `duration_cast`. Locale paths depend on deprecated codecvt and platform library behavior. Timezone formatting for `std::tm` depends on non-standard `tm_gmtoff` and `tm_zone` members when present; otherwise UTC fallbacks are used. Durations intentionally lack date information, so date specifiers are rejected. Negative time points with subseconds require careful second borrowing. Floating durations need NaN/Inf handling and precision validation.

## Test Signals

Tests should cover `%Q`, `%q`, `%H:%M:%S`, fractional seconds, padding modifiers, locale `L`, invalid date specifiers for durations, timezone specifiers with and without `tm_gmtoff`, safe-cast overflow, negative durations and time points, NaN/Inf floating durations, C++20 calendar formatters, and platform-specific `gmtime_r`/`gmtime_s` fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/chrono.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/color.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/color.h

## Purpose

This fmt header adds ANSI color and emphasis styling support. It defines named RGB colors, terminal color codes, text emphasis flags, a compact `text_style` representation, and formatting/printing helpers that wrap normal fmt output in ANSI escape sequences.

## Important APIs, types, and functions

Public types include `enum class color`, `enum class terminal_color`, `enum class emphasis`, `struct rgb`, and `class text_style`. Public helpers include `fg`, `bg`, `operator|` for styles/emphasis, styled overloads of `print`, `format`, `format_to`, and `vformat_to`, plus `styled(value, text_style)`.

Internal `detail::color_type` stores either unset, RGB, or terminal color state. `detail::ansi_color_escape<Char>` builds escape sequences for truecolor foreground/background, terminal colors, and emphasis combinations. `detail::styled_arg<T>` is a view wrapper with a formatter specialization that applies style only around a single argument.

## Control Flow

`text_style` bit-packs foreground, background, and emphasis into a 64-bit integer. `operator|=` checks for invalid OR combinations involving terminal colors by adding style words and testing overflow bits in the color discriminator regions, then merges with bitwise OR.

Formatting flow emits emphasis, foreground, and background escapes if present, delegates to normal `vformat_to` or an underlying `formatter<T>`, and appends `ESC[0m` when a style was applied. Terminal colors use SGR color codes; RGB colors use `38;2;r;g;b` or `48;2;r;g;b` sequences.

## State and Persistence Behavior

Styles are value objects. Formatting allocates temporary buffers for string-returning and file-printing overloads but does not persist global style state. The terminal state is reset after styled output when a non-empty style is used.

## Dependencies and Integration Points

It includes `format.h` and uses fmt buffers, `format_args`, `buffered_context`, `formatter`, `copy`, `print`, and `to_string`. It integrates with terminals that understand ANSI SGR escape sequences and with fmt's normal compile-time checked formatting APIs.

## Risks and Edge Cases

ANSI support is terminal-dependent; redirected output will contain raw escape bytes. OR-ing terminal colors with existing colors is rejected, but RGB foreground and background combinations are allowed. Emphasis constructor output assumes at least one emphasis bit when used through `has_emphasis`. Wide-character output uses templated `Char` escapes but actual terminal interpretation may still be byte-oriented. Resetting with `ESC[0m` clears all styles, not only those introduced by this call.

## Test Signals

Tests should verify exact escape sequences for RGB foreground/background, terminal colors, each emphasis bit, combined styles, reset emission, invalid terminal color OR errors, styled single-argument formatting, `format`, `format_to`, `print(FILE*)`, and behavior with empty/default `text_style`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/color.h -->
