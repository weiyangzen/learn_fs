# subset-b-009677 Research

Grouped source research for vendored Boost.ContainerHash, Boost.Core, Boost.Describe, Boost.Exception, and Boost.MP11 headers used by the mergerfs source tree. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_range.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_range.hpp

Purpose: Implements the internal `boost::hash_detail::hash_range(seed, first, last)` engine used by public `boost::hash_range` and range-based `hash_value` overloads. It provides a generic element-by-element path and optimized byte-range paths.

Important APIs, types, and functions: `is_char_type`, `read32le`, `read64le`, `mul32`, and overloaded `hash_range` templates selected by iterator value type, iterator category, and `std::size_t` width. Character-like inputs include `char`, signed/unsigned char, C++20 `char8_t`, and `std::byte` when available.

Control flow: Non-byte ranges loop over elements and call `hash_combine`. Byte ranges use fixed little-endian block readers, mix 4-byte chunks on 32-bit platforms or 8-byte chunks on 64-bit platforms, handle tail bytes without out-of-bounds reads, then finalize with multiplication/xor mixing.

State and persistence behavior: Stateless and header-only; the only carried state is the caller-provided seed and local mixing accumulators.

Dependencies and integration points: Depends on `hash_fwd.hpp`, `mulx.hpp`, iterator traits, integer limits, and C string memory helpers. Integrated by `hash.hpp` for strings, vectors, arrays, and generic containers.

Risks: Hash output is ABI/behavioral surface for unordered containers and persisted hash tests. Tail-byte and endian logic are sensitive, and optimized byte paths require valid iterator category/value-type detection.

Test signals: Compile under 32-bit and 64-bit targets; compare known hashes for empty, short, aligned, and unaligned byte ranges; verify non-random-access byte iterators; check that generic element ranges still call `hash_combine`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_tuple_like.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_tuple_like.hpp

Purpose: Adds hashing support for tuple-like types that expose `std::tuple_size` and `get<I>` but are not also detected as ranges.

Important APIs, types, and functions: `hash_combine_tuple_like<I,T>` recursively visits tuple elements, `hash_tuple_like(T const&)` builds a seed from element hashes, and the constrained `boost::hash_value(T const&)` overload enables tuple-like hashing through `container_hash::is_tuple_like`.

Control flow: Compile-time recursion stops when `I == tuple_size<T>::value`; otherwise it imports `std::get`, combines element `I`, and recurses to `I + 1`.

State and persistence behavior: No persistent state; the seed is local to one hash call.

Dependencies and integration points: Depends on `hash_fwd.hpp`, `is_tuple_like.hpp`, `is_range.hpp`, `<type_traits>`, and `<utility>`. Included by `hash.hpp` so `boost::hash` can use ADL-friendly tuple element access.

Risks: Ambiguity is avoided by excluding range types, but custom types that satisfy both tuple-like and range contracts rely on that ordering. Invalid `tuple_size`/`get` definitions fail at compile time.

Test signals: Compile and hash `std::tuple`, `std::pair`-like custom tuple types, `std::array` as a range rather than tuple path, and empty tuple-like types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_tuple_like.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/mulx.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/mulx.hpp

Purpose: Provides `boost::hash_detail::mulx`, a 64-bit multiplication helper that returns the xor of the low and high halves of a 128-bit product for hash mixing.

Important APIs, types, and functions: Single exported helper `mulx(std::uint64_t, std::uint64_t)`. Implementations use MSVC `_umul128` on x64, `__umulh` on MSVC ARM64, `__uint128_t` where available, or a portable 32-bit limb multiplication fallback.

Control flow: Preprocessor selects one implementation at compile time. Runtime flow is a straight multiplication and fold of high/low product bits.

State and persistence behavior: Stateless pure arithmetic helper.

Dependencies and integration points: Used by `hash_range.hpp` for 64-bit byte-range hashing and by other hash mixers that need wide-product diffusion. Depends on `<cstdint>` and MSVC intrinsics when relevant.

Risks: Fallback arithmetic must exactly emulate wide multiplication without overflow mistakes. Compiler/architecture detection affects both performance and hash output consistency.

Test signals: Cross-check `mulx` against `__uint128_t` on platforms that support it; compile MSVC x64/ARM64 and non-128-bit fallback paths; verify known values including zero, max, and mixed high-bit operands.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/mulx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash.hpp

Purpose: Main Boost.ContainerHash public implementation. It defines `boost::hash`, `hash_value` overloads for common C++ types, `hash_combine`, ordered/unordered range hashing, and conditional support for described classes, smart pointers, optional, variant, string view, system errors, and type indices.

Important APIs, types, and functions: `hash_value` overloads for enums, floating point, pointers, arrays, `std::complex`, `std::pair`, ranges, contiguous ranges, unordered ranges, described classes, smart pointers, `std::type_index`, `std::error_code`, `std::nullptr_t`, `std::optional`, `std::variant`, and `std::monostate`; public `hash_combine`, `hash_range`, `hash_unordered_range`; class template `boost::hash<T>`; specializations of `hash_is_avalanching` for strings/string views.

Control flow: Hash dispatch is overload/SFINAE driven. Floating point values are copied into integer words and normalized with `v + 0` to collapse negative zero. Ordered ranges combine sequentially; unordered ranges hash each element against the original seed and add commutatively. Described classes iterate base and member descriptors with MP11.

State and persistence behavior: Stateless header-only algorithms. Hash values are deterministic for a build/configuration but pointer/category-based hashes can vary by process and platform.

Dependencies and integration points: Central integration point for `hash_fwd`, range traits, tuple-like hashing, Boost.Describe, Boost.MP11, and standard library type support. mergerfs inherits this behavior through its vendored Boost include tree.

Risks: Hash output changes can affect container behavior, tests, and serialized hash assumptions. Pointer hashing depends on addresses; error category hashing uses category addresses; optional and monostate use arbitrary constants. Described unions are rejected by static assertion.

Test signals: Compile across C++03 through C++17 feature sets; verify known hashes for primitive, floating, string, vector, unordered set, tuple-like, optional, and variant inputs; test described class hashing with inherited members; check ADL `hash_value` extension behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_fwd.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_fwd.hpp

Purpose: Forward-declaration header for Boost.ContainerHash so clients can declare APIs without pulling the full hashing implementation.

Important APIs, types, and functions: Declares range traits in `boost::container_hash`, `boost::hash<T>`, `hash_combine`, `hash_range`, `hash_unordered_range`, and `hash_is_avalanching`.

Control flow: None; compile-time declarations only.

State and persistence behavior: No state.

Dependencies and integration points: Includes `<cstddef>` for `std::size_t`. Used by detail headers to avoid cycles and by public headers as a lightweight contract.

Risks: Signature drift with `hash.hpp` would break dependent headers. Forward declarations constrain later definitions and overload visibility.

Test signals: Include-order tests that include `hash_fwd.hpp` before and after `hash.hpp`; compile declarations in translation units that only need pointers/references to hash types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_fwd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_is_avalanching.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_is_avalanching.hpp

Purpose: Detects whether a hash function type advertises avalanching behavior.

Important APIs, types, and functions: `hash_is_avalanching<Hash>` public trait; internal `void_t`, `avalanching_value`, and `hash_is_avalanching_impl`. It supports both nested type `Hash::is_avalanching` and static data member `Hash::is_avalanching`; nested `void` is treated as true for legacy compatibility.

Control flow: Pure SFINAE trait selection at compile time.

State and persistence behavior: No state.

Dependencies and integration points: Included by `hash.hpp` and used by unordered/container code to identify quality of hash functions.

Risks: Treating nested `void` as true is compatibility behavior that can mask imprecise declarations. Static data member probing may instantiate surprising expressions for unusual hash types.

Test signals: Static assertions for no marker, nested `std::true_type`, nested `std::false_type`, nested `void`, and static constexpr bool markers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_is_avalanching.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_contiguous_range.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_contiguous_range.hpp

Purpose: Identifies range types whose elements can be hashed through contiguous memory via `data()` and `size()`.

Important APIs, types, and functions: Public `boost::container_hash::is_contiguous_range<T>`. Modern compilers use SFINAE to compare `begin/end` with `data/data+size`; old MSVC fallback specializes strings, vectors except `vector<bool>`, and arrays.

Control flow: Compile-time detection only. The trait gates the optimized `hash_value` overload in `hash.hpp`.

State and persistence behavior: No state.

Dependencies and integration points: Depends on `is_range.hpp`, Boost config/workaround headers, `<type_traits>`, and optionally standard containers. Integrates with `hash_range` byte fast paths.

Risks: Custom contiguous containers must satisfy the exact member expression pattern. False positives could hash memory with the wrong extent; false negatives fall back to element iteration. `vector<bool>` is explicitly non-contiguous for value hashing.

Test signals: Static assertions for `std::string`, `std::vector<int>`, `std::vector<bool>`, `std::array<T,N>`, const-qualified variants, and custom containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_contiguous_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_described_class.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_described_class.hpp

Purpose: Detects Boost.Describe-enabled class types that can be automatically hashed by member/base reflection.

Important APIs, types, and functions: Public `boost::container_hash::is_described_class<T>`, implemented as an integral constant over `boost::describe::has_describe_bases<T>` and `has_describe_members<T>`.

Control flow: Compile-time trait evaluation only.

State and persistence behavior: No state.

Dependencies and integration points: Depends on Boost.Describe bases and members headers plus `<type_traits>`. Used by `hash.hpp` to enable described-class `hash_value`.

Risks: A type needs both describe-bases and describe-members support; partial reflection metadata will not enable auto hashing. Unions are later rejected in `hash.hpp`.

Test signals: Static assertions for described struct/class, undescribed class, described union rejection through `hash_value`, and classes with inherited described bases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_described_class.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_range.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_range.hpp

Purpose: Detects types with `begin()` and `end()` members for generic range hashing.

Important APIs, types, and functions: Public `boost::container_hash::is_range<T>` and internal SFINAE helper `is_range_` over `std::declval<T const&>().begin()`/`.end()`.

Control flow: Compile-time detection only; true types select the range `hash_value` overloads.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash.hpp`, `hash_tuple_like.hpp`, and `is_contiguous_range.hpp`. Depends on `<type_traits>` and `<utility>`.

Risks: Only member `begin/end` are recognized; free-function range customization is not. Types with incidental `begin/end` may become hashable by range semantics.

Test signals: Static assertions for STL containers, const containers, custom member ranges, non-ranges, and free-only ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_tuple_like.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_tuple_like.hpp

Purpose: Detects tuple-like types for tuple element hashing.

Important APIs, types, and functions: Public `boost::container_hash::is_tuple_like<T>` driven by whether `std::tuple_size<T>::value` is well-formed.

Control flow: Compile-time SFINAE only.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash_tuple_like.hpp` and indirectly by `hash.hpp`. Depends on `<tuple>` and `<type_traits>`.

Risks: Detects tuple-size availability, not all `get<I>` validity; a type can pass this trait and still fail when hashed.

Test signals: Static assertions for `std::tuple`, `std::pair`, `std::array`, custom tuple-like types, and classes without tuple metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_tuple_like.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_unordered_range.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_unordered_range.hpp

Purpose: Detects unordered associative containers so hashing can be order-insensitive.

Important APIs, types, and functions: Public `boost::container_hash::is_unordered_range<T>`, implemented by detecting `typename T::hasher`.

Control flow: Compile-time SFINAE only; true types select `hash_unordered_range`.

State and persistence behavior: No state.

Dependencies and integration points: Used by `hash.hpp` to distinguish ordered ranges from unordered containers.

Risks: The `hasher` nested type is a heuristic. Custom ordered containers with a `hasher` alias could be misclassified; unordered containers without that alias will hash order-sensitively.

Test signals: Static assertions for `std::unordered_set/map`, ordered containers, and custom containers with/without `hasher`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/container_hash/is_unordered_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/addressof.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/addressof.hpp

Purpose: Portable implementation of `boost::addressof`, bypassing overloaded `operator&` and using compiler builtins when available.

Important APIs, types, and functions: Public `addressof(T&)`; deleted rvalue overload when supported; internal `addrof`, `addrof_ref`, constexpr-detection helpers, and null pointer specializations.

Control flow: Compile-time selection uses `__builtin_addressof` when supported, otherwise chooses constexpr plain `&o` only when no overloaded address operator exists, falling back to the classic char-reference reinterpretation trick.

State and persistence behavior: Stateless pointer utility.

Dependencies and integration points: Used widely by Boost.Core and allocator/pointer utilities. Depends on Boost config/workaround and `<cstddef>` in fallback mode.

Risks: Fallback paths are compiler-workaround-heavy and touch strict-aliasing-sensitive code. Array and null pointer edge cases have special handling for old compilers.

Test signals: Address objects with overloaded member and non-member `operator&`, arrays, const/volatile/nullptr types, constexpr cases, and deleted rvalue behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/addressof.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/allocator_access.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/allocator_access.hpp

Purpose: Backports allocator-traits style type discovery and operations for allocators across old and modern C++ modes.

Important APIs, types, and functions: Type traits for allocator value/pointer/const pointer/void pointer/difference/size types, propagation traits, `allocator_is_always_equal`, `allocator_rebind`, and alias templates. Operation helpers include `allocator_allocate`, `allocator_deallocate`, `allocator_construct`, `allocator_destroy`, `allocator_max_size`, `allocator_select_on_container_copy_construction`, `allocator_construct_n`, and `allocator_destroy_n`.

Control flow: SFINAE detects optional allocator members (`pointer`, `construct`, `destroy`, `max_size`, `select_on_container_copy_construction`, hinted `allocate`). Fallbacks use placement new, destructor calls, numeric limit max size, and allocator copy. Bulk construction uses `detail::alloc_destroyer` RAII so partially constructed ranges are destroyed on exception.

State and persistence behavior: No persistent global state. Temporary state is the `alloc_destroyer` count tracking constructed elements during a bulk operation.

Dependencies and integration points: Depends on `pointer_traits.hpp`, Boost config, `<limits>`, `<new>`, `<type_traits>`, and `<utility>`. Exposed through `allocator_traits.hpp`.

Risks: Old-compiler branches and deprecated allocator member detection are fragile. Construction fallback must preserve exception safety and forwarding semantics. Incorrect rebinding can break fancy-pointer allocators.

Test signals: Custom allocator with full traits, minimal allocator, allocator with fancy pointer, throwing element construction for cleanup, hinted allocate present/absent, and old C++ compatibility builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/allocator_access.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/allocator_traits.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/allocator_traits.hpp

Purpose: Public `boost::allocator_traits` facade over the lower-level allocator access helpers.

Important APIs, types, and functions: `allocator_traits<A>` exposes standard allocator typedefs, `rebind_traits`, and static `allocate`, `deallocate`, `construct`, `destroy`, `max_size`, and `select_on_container_copy_construction`.

Control flow: Each static member forwards directly to the matching `boost::allocator_*` helper, inheriting that helper's SFINAE/fallback behavior.

State and persistence behavior: Stateless traits facade.

Dependencies and integration points: Includes `allocator_access.hpp`. Used by containers or utilities that want a Boost-provided allocator-traits interface independent of standard library support.

Risks: Must remain a thin alias-compatible facade; mismatches with `allocator_access` typedefs or forwarding overloads can affect allocator-aware containers.

Test signals: Compile with minimal and custom allocators; verify `rebind_traits`; exercise construction/destruction and max-size forwarding against `allocator_access` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/allocator_traits.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/bit.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/bit.hpp

Purpose: Portable Boost.Core backport of C++20 `<bit>` utilities.

Important APIs, types, and functions: `bit_cast`, `countl_zero`, `countl_one`, `countr_zero`, `countr_one`, `popcount`, `rotl`, `rotr`, `has_single_bit`, `bit_width`, `bit_floor`, `bit_ceil`, `endian`/`endian_type`, and `byteswap`.

Control flow: Compile-time configuration selects compiler builtins and intrinsics for GCC/Clang/MSVC, with constexpr arithmetic fallbacks. Public functions assert integer/unsigned constraints where required, dispatch by integer width, and handle zero cases explicitly.

State and persistence behavior: Stateless arithmetic utilities.

Dependencies and integration points: Depends on Boost static assert/config/cstdint, `<limits>`, `<cstring>`, and `<cstdlib>`. Used by hashing, serialization, endian-sensitive code, and general Boost utilities.

Risks: Undefined behavior risks are avoided by width checks and `memcpy`/builtin bit_cast, but shift/rotation and `bit_ceil` overflow boundaries need care. Endian detection is platform macro dependent.

Test signals: Static and runtime tests for all unsigned widths; zero/all-ones values; rotation counts larger than bit width and negative counts; endian enum on supported platforms; byteswap known constants; constexpr compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/bit.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_pause.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_pause.hpp

Purpose: Low-level spin-wait pause primitive for Boost smart pointer and concurrency internals.

Important APIs, types, and functions: `boost::core::sp_thread_pause()` emits architecture-specific pause/yield instructions through `BOOST_CORE_SP_PAUSE`.

Control flow: Preprocessor chooses x86 `_mm_pause`/`pause`, ARM `yield`, MSVC intrinsics, or an empty fallback. Runtime function is a single forced-inline instruction/macro invocation.

State and persistence behavior: No state.

Dependencies and integration points: Included by `yield_primitives.hpp` and fallback `sp_thread_yield.hpp`. Depends on Boost config and compiler architecture macros.

Risks: Incorrect architecture detection can emit unsupported assembly or lose spin-loop performance. Empty fallback is correct but may waste CPU under contention.

Test signals: Compile x86, ARM, MSVC, GCC/Clang paths; inspect generated assembly or run smoke tests in spin-wait code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_pause.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_sleep.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_sleep.hpp

Purpose: Provides `sp_thread_sleep`, a short backoff sleep primitive for spin/yield loops.

Important APIs, types, and functions: `boost::core::sp_thread_sleep()` and compatibility `boost::detail::sp_thread_sleep` alias on Windows.

Control flow: Windows calls `Sleep(1)`. POSIX with `nanosleep` sleeps for a small timespec and may optionally block/unblock SIGCHLD around the call for pthread platforms. Fallback delegates to `sp_thread_yield`.

State and persistence behavior: No persistent state; POSIX branch temporarily manipulates thread signal masks.

Dependencies and integration points: Depends on Boost config, Windows sleep shim, `<time.h>`, optional pthread/signal headers, or yield fallback. Included by `yield_primitives.hpp`.

Risks: Signal-mask handling must restore prior state. Sleep duration and platform availability affect contention backoff behavior. Android/OHOS paths avoid pthread signal logic.

Test signals: Compile Windows, nanosleep, and fallback branches; runtime smoke test that call returns; signal-mask preservation test on pthread targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_sleep.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_yield.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_yield.hpp

Purpose: Provides a portable thread-yield primitive for spin/backoff code.

Important APIs, types, and functions: `boost::core::sp_thread_yield()` and Windows compatibility alias in `boost::detail`.

Control flow: Windows calls `SwitchToThread`. POSIX with scheduler support calls `sched_yield`. Fallback calls `sp_thread_pause`.

State and persistence behavior: No state.

Dependencies and integration points: Uses `sp_win32_sleep.hpp`, `<sched.h>`/AIX headers, or `sp_thread_pause.hpp`. Included by `yield_primitives.hpp` and sleep fallback.

Risks: Yield semantics vary by scheduler; fallback pause is not a true OS yield. AIX include path differs.

Test signals: Compile all platform branches; basic runtime call; integration with spin lock/backoff tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_yield.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_win32_sleep.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_win32_sleep.hpp

Purpose: Minimal Win32 declarations for `Sleep` and `SwitchToThread` without requiring `windows.h`, unless `BOOST_USE_WINDOWS_H` is requested.

Important APIs, types, and functions: Declares imported `Sleep(unsigned long)` and `SwitchToThread()` with the correct calling convention for supported Windows/Cygwin configurations.

Control flow: Preprocessor either includes `<windows.h>` or emits `extern "C" __declspec(dllimport)` declarations.

State and persistence behavior: No state.

Dependencies and integration points: Used by `sp_thread_sleep.hpp` and `sp_thread_yield.hpp`.

Risks: Calling convention and type-width macros are platform sensitive, especially Cygwin 64-bit and Clang x64. Declaration drift with Windows headers would break linkage.

Test signals: Compile with and without `BOOST_USE_WINDOWS_H` on MSVC, MinGW/Cygwin, and Clang-cl; link a small program calling sleep/yield primitives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_win32_sleep.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/static_assert.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/detail/static_assert.hpp

Purpose: Internal static assertion macro wrapper for Boost.Core.

Important APIs, types, and functions: Defines `BOOST_CORE_STATIC_ASSERT(expr)` as `static_assert(expr, #expr)` where available or `BOOST_STATIC_ASSERT(expr)` on older compilers.

Control flow: Compile-time preprocessor selection only.

State and persistence behavior: No state.

Dependencies and integration points: Includes Boost config and, for old compilers, Boost.StaticAssert. Used by `bit.hpp` and other core headers.

Risks: Error message differences across compiler modes; macro must be usable in class/function scopes.

Test signals: Compile passing and failing assertions in C++03 and C++11+ modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/detail/static_assert.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/empty_value.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/empty_value.hpp

Purpose: Provides `boost::empty_::empty_value<T,N>` storage wrapper that applies empty-base optimization when safe.

Important APIs, types, and functions: `use_empty_value_base<T>`, `empty_init_t`, `empty_value<T,N,UseBase>`, `empty_value_base<T>`, `boost::empty_::empty_value`, and inline constant `boost::empty_init`.

Control flow: Compile-time trait chooses composition or private inheritance. Constructors support default/empty-init and forwarding where available. Accessors return references to the stored value/base.

State and persistence behavior: Stores one `T` value unless represented by empty base subobject. No external persistence.

Dependencies and integration points: Depends on Boost config, type traits, and utility forwarding. Used by containers and utilities to store allocators, predicates, or functors compactly.

Risks: Empty-base optimization must avoid final/non-empty/unsafe types and preserve object identity for repeated bases via `N`. Constructor forwarding differs by language mode.

Test signals: Size tests for empty vs non-empty types, multiple `N` indices, final classes, const accessors, forwarding constructors, and standard-layout expectations where relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/empty_value.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/ignore_unused.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/ignore_unused.hpp

Purpose: Small utility to suppress unused variable warnings.

Important APIs, types, and functions: `boost::ignore_unused()` overloads for no arguments, one argument, and variadic arguments where supported.

Control flow: Runtime functions do nothing; they cast/use arguments only enough to satisfy compilers.

State and persistence behavior: No state.

Dependencies and integration points: Uses Boost config for variadic/rvalue support. Widely usable by headers that intentionally ignore parameters in portable code.

Risks: Must not evaluate arguments more than normal function-call evaluation; cannot suppress unused type/template warnings.

Test signals: Compile with high warning levels for ignored local variables and parameters across C++03/C++11 modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/ignore_unused.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/no_exceptions_support.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/no_exceptions_support.hpp

Purpose: Macros that let Boost code write try/catch cleanup blocks that compile away when exceptions are disabled.

Important APIs, types, and functions: `BOOST_TRY`, `BOOST_CATCH(x)`, `BOOST_RETHROW`, `BOOST_CATCH_END`, and legacy support for `BOOST_NO_EXCEPTIONS`.

Control flow: With exceptions, macros expand to `try`, `catch`, and `throw`. Without exceptions, catch blocks become unreachable/disabled constructs and rethrow is omitted or adapted.

State and persistence behavior: No state.

Dependencies and integration points: Used by Boost components that support `BOOST_NO_EXCEPTIONS` builds while sharing one source body.

Risks: Cleanup paths hidden behind catch macros do not execute in no-exception mode. Macro syntax must remain balanced.

Test signals: Compile the same source with and without exception support; verify cleanup behavior in exception-enabled mode and syntax in disabled mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/no_exceptions_support.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/noncopyable.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/noncopyable.hpp

Purpose: Defines `boost::noncopyable`, a base class that disables copy construction and copy assignment.

Important APIs, types, and functions: `boost::noncopyable` and implementation namespace `boost::noncopyable_::noncopyable`.

Control flow: No runtime flow; copy operations are deleted in modern compilers or private/unimplemented in older compilers.

State and persistence behavior: Empty base type with no state.

Dependencies and integration points: Used by classes that need noncopyable semantics without including heavier Boost headers.

Risks: Inheritance affects type traits and aggregate behavior; old compiler private declarations produce different diagnostics than deleted functions.

Test signals: Static assertions or compile-fail checks for copy construction/assignment and size/EBO behavior when used as a base.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/noncopyable.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/nvp.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/nvp.hpp

Purpose: Lightweight name-value-pair wrapper used by Boost serialization-facing code without depending on full Boost.Serialization.

Important APIs, types, and functions: `boost::serialization::nvp<T>`, `make_nvp(char const*, T&)`, and exposed aliases in `boost::core` through `serialization.hpp`.

Control flow: Construction stores a name pointer and value reference/pointer; archive operators can inspect name and value.

State and persistence behavior: Holds non-owning references to a name string and value. It does not serialize by itself.

Dependencies and integration points: Used by `boost/core/serialization.hpp` and code that needs a minimal archive adapter.

Risks: Name and value lifetimes must outlive the wrapper. It is a compatibility shim, not a full serialization implementation.

Test signals: Compile archive code using `make_nvp`, const/non-const values, and integration through `boost::core` aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/nvp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/pointer_traits.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/pointer_traits.hpp

Purpose: Portable implementation of pointer traits for raw and fancy pointer types.

Important APIs, types, and functions: `boost::pointer_traits<T>`, raw pointer specialization, nested `element_type`, `difference_type`, `rebind_to<U>`, and static `pointer_to`. Also exposes `to_address` overloads for raw and fancy pointers when supported.

Control flow: SFINAE derives element type from `T::element_type` or first template argument, derives difference type from `T::difference_type` or `std::ptrdiff_t`, and chooses `T::rebind<U>` or template rebinding. `pointer_to` calls pointer-specific `pointer_to` or raw `addressof`.

State and persistence behavior: No state.

Dependencies and integration points: Used by allocator access and container internals that support fancy pointers. Depends on `addressof.hpp` and Boost config.

Risks: Template rebinding is heuristic for custom pointer templates. `to_address` recursion depends on pointer-like `operator->`. Void pointer handling is special.

Test signals: Static assertions for raw pointers, smart/fancy pointer mocks, rebind behavior, pointer_to address identity, and `to_address` through nested pointer wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/pointer_traits.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/serialization.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/serialization.hpp

Purpose: Minimal serialization adapter utilities for Boost.Core users that need split load/save dispatch without taking a full serialization dependency.

Important APIs, types, and functions: Forward declarations for `boost::serialization::version`, `access`, `nvp`; `core_version_type`; `boost::core::split_free`, `split_member`, `load_construct_data_adl`, and `save_construct_data_adl`; internal `load_or_save_f` and `load_or_save_m`.

Control flow: `split_free` and `split_member` inspect `Archive::is_saving::value` at compile time and call either `save`/`load` free functions or member functions through `serialization::access`.

State and persistence behavior: No state; all persistence belongs to the archive and serialized object.

Dependencies and integration points: Includes `nvp.hpp`. Integrates with archive types that expose `is_saving` and Boost.Serialization conventions.

Risks: Requires exact archive traits and access hooks. ADL construction hooks are no-ops by default and need customization elsewhere for non-default construction.

Test signals: Mock saving/loading archives, split free/member functions, version propagation, and ADL override checks for construct data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/serialization.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/yield_primitives.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/core/yield_primitives.hpp

Purpose: Aggregating header for Boost.Core spin/yield/sleep primitives.

Important APIs, types, and functions: Includes `sp_thread_pause`, `sp_thread_yield`, and `sp_thread_sleep`.

Control flow: None in this header; behavior comes from included platform detail headers.

State and persistence behavior: No state.

Dependencies and integration points: Public include point for code that needs all backoff primitives.

Risks: Pulls platform-specific declarations into translation units; include-order issues would surface from detail headers.

Test signals: Include-only compile test and smoke calls to the three primitives on supported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/core/yield_primitives.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/cstdint.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/cstdint.hpp

Purpose: Boost portable fixed-width integer typedef and integer literal macro header.

Important APIs, types, and functions: Defines/imports `boost::int8_t` through `uint_fast64_t`, `intmax_t`, `uintmax_t`, optional `intptr_t`/`uintptr_t` with `BOOST_HAS_INTPTR_T`, `BOOST_NO_INT64_T`, and C99-style `INT*_C`/`UINT*_C` macros when missing.

Control flow: Preprocessor chooses system `<stdint.h>`/`<inttypes.h>` when reliable, old platform-specific branches, or hand-written typedefs based on `<limits.h>` widths. A post-include macro section fills constant macros.

State and persistence behavior: Compile-time typedef/macro definitions only.

Dependencies and integration points: Used by Boost.Core bit utilities, hashing, and any vendored Boost code needing fixed-width integers.

Risks: Highly platform-sensitive; wrong width detection is a compile-time hard error or ABI mismatch. Literal macros differ for MS/Borland suffixes, long, and long long.

Test signals: Compile on representative Windows, Linux, BSD, macOS, and old-compiler configurations; static assert widths and signedness; compile integer literal macros at boundary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/cstdint.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/current_function.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/current_function.hpp

Purpose: Defines `BOOST_CURRENT_FUNCTION`, a portable macro for the current function signature/name.

Important APIs, types, and functions: Macro `BOOST_CURRENT_FUNCTION`; internal `boost::detail::current_function_helper()` scopes the preprocessor definitions.

Control flow: Preprocessor chooses `__PRETTY_FUNCTION__`, `__FUNCSIG__`, `__FUNCTION__`, `__FUNC__`, `__func__`, or `"(unknown)"` based on compiler and `BOOST_DISABLE_CURRENT_FUNCTION`.

State and persistence behavior: No state.

Dependencies and integration points: Used by assertions, diagnostics, exceptions, and logging helpers.

Risks: Macro expands to different string formats by compiler, affecting diagnostics and tests that compare exact messages.

Test signals: Compile on major compilers; verify macro is defined inside functions and respects `BOOST_DISABLE_CURRENT_FUNCTION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/current_function.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/bases.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/bases.hpp

Purpose: Provides Boost.Describe base-class descriptor querying.

Important APIs, types, and functions: `describe_bases<T,M>`, `has_describe_bases<T>`, internal `_describe_bases<T>`, and `base_filter<M>`.

Control flow: For C++11-capable configurations, ADL probes `boost_base_descriptor_fn(static_cast<T**>(0))` and MP11 filters descriptor lists by requested access modifiers.

State and persistence behavior: Compile-time metadata only.

Dependencies and integration points: Depends on `modifiers.hpp`, `void_t.hpp`, config, MP11 algorithm, and type traits. Used by described-class hashing in `hash.hpp` and member inheritance traversal.

Risks: Requires generated/declared descriptor functions from Boost.Describe macros. Missing metadata produces SFINAE false rather than runtime failure.

Test signals: Static assertions for described and undescribed bases, modifier filtering, virtual base metadata, and C++03 disabled path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/bases.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/config.hpp

Purpose: Central feature/configuration macros for Boost.Describe.

Important APIs, types, and functions: Defines `BOOST_DESCRIBE_CXX11`, `BOOST_DESCRIBE_CXX14`, `BOOST_DESCRIBE_CONSTEXPR_OR_CONST`, `BOOST_DESCRIBE_MAYBE_UNUSED`, `BOOST_DESCRIBE_INLINE_VARIABLE`, and `BOOST_DESCRIBE_INLINE_CONSTEXPR`.

Control flow: Preprocessor detects language level, MSVC support, GCC 4.7 exclusion, Clang unused attributes, and inline variables.

State and persistence behavior: Compile-time macros only.

Dependencies and integration points: Included by all Boost.Describe headers to gate reflection metadata support.

Risks: Incorrect C++ level detection changes whether describe APIs exist at all. Inline variable support affects ODR behavior for descriptor constants.

Test signals: Compile C++03, C++11, C++14, and C++17 modes; verify macro values and descriptor definitions on MSVC/GCC/Clang.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/cx_streq.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/cx_streq.hpp

Purpose: Provides constexpr string equality for descriptor names.

Important APIs, types, and functions: `boost::describe::detail::cx_streq(char const*, char const*)`.

Control flow: Recursively compares current characters and advances until mismatch or null terminator.

State and persistence behavior: No state.

Dependencies and integration points: Used by `members.hpp` to detect hidden inherited members by descriptor name.

Risks: Recursive constexpr depth depends on string length and compiler support; expects valid null-terminated strings.

Test signals: Static assertions for equal strings, unequal strings, prefix cases, empty strings, and descriptor-name hiding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/cx_streq.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/void_t.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/void_t.hpp

Purpose: Local `void_t` implementation for Boost.Describe SFINAE probes.

Important APIs, types, and functions: `make_void<T...>` and alias `void_t<T...>`.

Control flow: Compile-time alias substitution only.

State and persistence behavior: No state.

Dependencies and integration points: Included by Describe base/member detection headers.

Risks: Available only when `BOOST_DESCRIBE_CXX11` is defined; dependent headers must guard usage accordingly.

Test signals: Static SFINAE probes for valid/invalid descriptor expressions in C++11+ mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/detail/void_t.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/members.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/members.hpp

Purpose: Provides Boost.Describe member descriptor querying, including inherited member traversal and modifier filtering.

Important APIs, types, and functions: `describe_members<T,M>`, `has_describe_members<T>`, `_describe_public_members`, `_describe_protected_members`, `_describe_private_members`, `describe_inherited_members`, `member_filter`, `update_modifiers`, virtual-base tracking helpers, and hidden-name detection.

Control flow: Descriptor lists are acquired through ADL functions, appended with MP11, optionally expanded through base descriptors, and filtered by modifier flags. Inherited descriptors update access modifiers, add `mod_inherited`, and mark hidden members when derived classes declare the same name.

State and persistence behavior: Compile-time metadata only.

Dependencies and integration points: Depends on `modifiers.hpp`, `bases.hpp`, `cx_streq.hpp`, MP11 algorithm/utility/integral/list/bind, and type traits. Used by ContainerHash described-class hashing.

Risks: Descriptor pointer/name static members must obey ODR rules on older compilers. Inherited/virtual base traversal must avoid duplicate virtual base visits and correctly flag hidden members.

Test signals: Static assertions for public/protected/private filters, inherited and virtual base members, hidden-name flags, function vs data descriptors, and described/undescribed classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/members.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/modifiers.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/describe/modifiers.hpp

Purpose: Defines bitmask constants describing Boost.Describe member/base metadata.

Important APIs, types, and functions: Modifier constants such as `mod_public`, `mod_protected`, `mod_private`, `mod_virtual`, `mod_static`, `mod_function`, `mod_any_access`, `mod_inherited`, `mod_hidden`, and related masks.

Control flow: None; constants only.

State and persistence behavior: No state.

Dependencies and integration points: Used by `bases.hpp`, `members.hpp`, and consumers such as `hash.hpp` to filter descriptor lists.

Risks: Values are bitmask contract; changing them breaks descriptor filtering and external code using masks.

Test signals: Static assertions for mask combinations and filtering behavior in base/member describe APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/describe/modifiers.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/exception/exception.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/exception/exception.hpp

Purpose: Core Boost.Exception type and helpers for attaching diagnostic data and enabling exception cloning/current-exception support.

Important APIs, types, and functions: `boost::exception`, `error_info<Tag,T>` specializations for throw function/file/line/column, `enable_error_info`, `enable_current_exception`, internal `refcount_ptr`, `error_info_container`, `error_info_injector<T>`, `clone_base`, `clone_impl<T>`, `copy_boost_exception`, and throw-location retrieval.

Control flow: `set_info` friend helpers mutate diagnostic fields. `enable_error_info` conditionally wraps non-Boost exception types in an injector that also derives from `boost::exception`. `enable_current_exception` wraps copyable exceptions in `clone_impl`, whose virtual `clone` copies Boost.Exception metadata and whose `rethrow` throws or calls `boost::throw_exception` when exceptions are disabled.

State and persistence behavior: `boost::exception` stores mutable ref-counted diagnostic container plus throw function/file/line/column fields. State persists with copied/cloned exception objects.

Dependencies and integration points: Depends on source location, Boost config, `<exception>`, and either `boost::shared_ptr` or `std::shared_ptr` in mini-Boost mode. Used by Boost throw/catch diagnostics.

Risks: Mutable diagnostic state inside exception objects is delicate. Refcount and clone ownership must avoid leaks/double releases. No-exception mode depends on user-provided `throw_exception`.

Test signals: Attach/retrieve throw metadata, copy and clone exceptions, rethrow with current-exception wrapper, no-exception compile path, mini-Boost shared_ptr mode, and source-location extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/exception/exception.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/limits.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/limits.hpp

Purpose: Compatibility wrapper around `<limits>` plus fallback `std::numeric_limits` specializations for long long on old standard libraries.

Important APIs, types, and functions: Includes either `<limits>` or `<limits.h>` depending on Boost config; conditionally specializes `std::numeric_limits` for `boost::long_long_type` and `boost::ulong_long_type`.

Control flow: Preprocessor selects standard limits support or hand-written min/max/digits/signedness values using compiler macros.

State and persistence behavior: Compile-time traits only.

Dependencies and integration points: Used by `cstdint.hpp` and other Boost code needing numeric limits on legacy platforms.

Risks: Specializing in namespace `std` is only for missing implementation support and must match actual type widths. Incorrect LLONG/ULLONG macro detection breaks numeric traits.

Test signals: Static assertions for numeric_limits values and digits for signed/unsigned long long under legacy config macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/limits.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/algorithm.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/algorithm.hpp

Purpose: Large Boost.MP11 compile-time algorithm suite for type and value lists.

Important APIs, types, and functions: Includes transform/filter/fill/repeat/product/drop/iota/at/take/slice/back/pop/replace/remove/flatten/partition/sort/nth/find/reverse/fold/unique/all/none/any/replace_at/for_each/insert/erase/starts_with/rotate/power_set/partial_sum/iterate/pairwise/sliding/intersperse/split/join algorithms, plus `_q` quote variants.

Control flow: All algorithms are template metaprograms. Many use pack expansions, MP11 list primitives, `mp_fold`, `mp_append`, constexpr arrays for find/count, quicksort-like partitioning for sort/nth, and runtime `mp_for_each` that invokes a callable once per type object.

State and persistence behavior: Compile-time type/value transformations only; `mp_for_each` passes a runtime callable through repeated invocations but stores no global state.

Dependencies and integration points: Central dependency for Boost.Describe and ContainerHash described-class hashing. Depends on MP11 list/set/integral/utility/function and detail primitives.

Risks: Template instantiation depth and compiler workaround branches are key risks. Size mismatches in multi-list transform produce sentinel errors. Algorithms on empty lists can intentionally fail where no element exists.

Test signals: MP11 static assertion suite covering each algorithm, value-list support, large lists, MSVC/CUDA/GCC workaround configurations, and `mp_for_each` runtime invocation order.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/algorithm.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/bind.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/bind.hpp

Purpose: Provides MP11 metafunction binding and placeholders.

Important APIs, types, and functions: `mp_bind_front`, `mp_bind_back`, `_1` through `_9`, `mp_arg<I>`, `mp_bind`, and `_q` variants.

Control flow: Bound arguments are evaluated at template instantiation time. Placeholders select call-site arguments; nested binds and front/back binds are recursively evaluated before applying the target metafunction.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Depends on `algorithm.hpp`, `utility.hpp`, and `<cstddef>`. Used by Describe member filtering and user MP11 expressions.

Risks: Alias-template expansion limitations require `mp_defer`; incorrect placeholder index produces an out-of-range `mp_at_c` error. Nested bind complexity can increase diagnostics.

Test signals: Static assertions for front/back binding, placeholders, nested bind expressions, quote variants, and invalid placeholder arity diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/bind.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/config.hpp

Purpose: Compiler/language feature detection and workaround definitions for Boost.MP11.

Important APIs, types, and functions: `BOOST_MP11_WORKAROUND`, compiler version macros for CUDA/Clang/Intel/GCC/MSVC, `BOOST_MP11_CONSTEXPR`, and feature flags such as constexpr availability, fold expressions, template auto, type-pack element, and C++14 constexpr.

Control flow: Preprocessor maps compiler predefined macros into normalized MP11 feature macros and disables/enables workarounds.

State and persistence behavior: Compile-time macros only.

Dependencies and integration points: Included by all MP11 detail and algorithm headers.

Risks: Incorrect feature detection changes template implementations and can break old compiler support. Some workarounds deliberately include unusual declarations such as `gets` for old Clang/libstdc++ combinations.

Test signals: Compile MP11 suite under supported compiler matrix; assert feature macros in representative modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/config.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_append.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_append.hpp

Purpose: Implements `mp_append`, the foundational list concatenation primitive for type and value lists.

Important APIs, types, and functions: Internal `mp_append_impl`, `append_11_impl`, `append_value_impl`, `append_type_lists`, `append_value_lists`, and public alias `mp_append<L...>`.

Control flow: Template specializations concatenate list packs, batching groups of up to eleven lists to reduce instantiation depth. With template-auto support, value-list concatenation is selected when all inputs are value lists; otherwise type-list concatenation is used.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used throughout MP11 algorithms, Describe metadata accumulation, and ContainerHash described-class support.

Risks: Mixed type/value lists are intentionally not value-concatenated. Compiler workaround branches for MSVC and CUDA must preserve behavior.

Test signals: Static assertions for zero/one/many lists, large list batches, value-list concatenation, mixed list rejection/typing, and old compiler workaround builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_append.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_copy_if.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_copy_if.hpp

Purpose: Implements `mp_copy_if`, filtering a list by predicate while preserving the original list template.

Important APIs, types, and functions: `detail::mp_copy_if_impl`, public `mp_copy_if<L,P>`, and `mp_copy_if_q<L,Q>`.

Control flow: For each element, template `_f` maps matching elements to singleton `mp_list<U>` and nonmatches to `mp_list<>`; `mp_append` then flattens the results into the output list.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 algorithms and Boost.Describe descriptor filtering.

Risks: Predicate must expose a boolean `value`. Old MSVC branch uses nested `::type` indirection.

Test signals: Static assertions for empty lists, all/none/some matches, quote variants, and preserving list template.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_copy_if.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_count.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_count.hpp

Purpose: Implements compile-time element counting and predicate counting.

Important APIs, types, and functions: `mp_count<L,V>`, `mp_count_if<L,P>`, `mp_count_if_q<L,Q>`, and constexpr helpers `cx_plus`, `cx_count`, `cx_count_if`.

Control flow: Preferred implementations use constexpr bool arrays and loops or recursive constexpr addition; fallback uses `mp_plus` over boolean integral constants.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 algorithms, `mp_append` value-list selection, and logical predicates.

Risks: Compiler constexpr support changes implementation. Predicate values must be convertible to bool.

Test signals: Static assertions for duplicates, missing elements, empty lists, predicate counts, large lists, and no-constexpr fallback builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_count.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_defer.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_defer.hpp

Purpose: Provides deferred/evaluable metafunction primitives used to avoid premature hard errors in MP11.

Important APIs, types, and functions: `mp_if_c`, `mp_if`, `mp_valid`, `mp_defer`, `mp_eval_or`, `mp_eval_if`, `mp_eval_if_c`, `mp_cond`, and related implementation helpers.

Control flow: Template selection delays instantiation of branches until selected or proven valid. `mp_valid` detects whether `F<T...>` is well-formed, with alternate implementation for Intel.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Core building block for MP11 utility, bind, algorithms, and SFINAE-heavy Boost headers.

Risks: Incorrect deferral causes eager instantiation and noisy compile failures. Branch arity and selected fallback types must match expected alias contracts.

Test signals: Static assertions for valid/invalid expressions, branch laziness, default fallbacks, conditional chains, Intel workaround builds, and alias-template failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_defer.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_fold.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_fold.hpp

Purpose: Implements left fold over MP11 lists.

Important APIs, types, and functions: `mp_fold<L,V,F>`, `mp_fold_q<L,V,Q>`, `mp_fold_impl`, and unrolled helper structs `mp_fold_Q1` through `mp_fold_Q9`.

Control flow: Converts input to `mp_list`, handles empty list as initial value, unrolls up to nine elements, and recursively folds groups of ten for longer lists to manage instantiation depth.

State and persistence behavior: Compile-time accumulator type only.

Dependencies and integration points: Used by MP11 min/max, unique, partial sums, Describe inherited metadata processing, and many algorithms.

Risks: Metafunction `F` must accept accumulator and element in the expected order. Very large lists can still stress compiler template depth.

Test signals: Static assertions for empty, single, short, and long lists; quote variant; accumulator order; old MSVC workaround mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_fold.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_front.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_front.hpp

Purpose: Implements `mp_front`, retrieving the first element of a type or value list.

Important APIs, types, and functions: `detail::mp_front_impl<L>` and public alias `mp_front<L>`. Value-list support wraps the first value in `mp_value<A>`.

Control flow: Template specialization matches non-empty list templates; empty/non-list inputs intentionally lack `type`.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by algorithms such as fold, min/max, map find, sort, and bind.

Risks: Empty list use is a hard compile error by design; value-list behavior depends on template-auto support.

Test signals: Static assertions for `mp_list<T...>`, standard tuple-like type lists, value lists, and compile-fail empty list behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_front.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_list.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_list.hpp

Purpose: Detects whether a type is an instantiation of a type-template list.

Important APIs, types, and functions: `mp_is_list<L>`.

Control flow: Primary template returns `mp_false`; specialization for `template<class...> class L, class... T` returns `mp_true`.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by MP11 list utilities and validation paths.

Risks: Value lists are not type lists; fixed-arity templates may not match unless expressible as variadic template patterns.

Test signals: Static assertions for `mp_list`, `std::tuple`, non-list types, and value-list types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_list.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_value_list.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_value_list.hpp

Purpose: Detects whether a type is an instantiation of a template-auto value list.

Important APIs, types, and functions: `mp_is_value_list<L>`.

Control flow: Primary template returns false; when `BOOST_MP11_HAS_TEMPLATE_AUTO` is available, `template<auto...>` specializations return true.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by `mp_append` to choose value-list concatenation.

Risks: Disabled entirely on compilers without template-auto support. Mixed lists require careful algorithm selection.

Test signals: Static assertions for `mp_list_v<...>`, type lists, non-list types, and feature-disabled builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_is_value_list.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list.hpp

Purpose: Defines the fundamental MP11 type-list container.

Important APIs, types, and functions: `template<class... T> struct mp_list`.

Control flow: None; it is an empty variadic type wrapper.

State and persistence behavior: Compile-time type container only.

Dependencies and integration points: Used throughout MP11 and Boost.Describe metadata lists.

Risks: No direct risks beyond preserving the empty-list type identity expected by algorithms.

Test signals: Static assertions that algorithms accept and preserve `mp_list` shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list_v.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list_v.hpp

Purpose: Defines the fundamental MP11 value-list container for `template<auto...>` values.

Important APIs, types, and functions: `template<auto... A> struct mp_list_v`, available only when `BOOST_MP11_HAS_TEMPLATE_AUTO` is set.

Control flow: None; compile-time value wrapper.

State and persistence behavior: Compile-time value container only.

Dependencies and integration points: Used by value-list aware MP11 primitives such as `mp_append`, `mp_front`, and `mp_transform`.

Risks: Feature-gated; clients must not rely on it in pre-C++17/template-auto modes.

Test signals: Compile value-list algorithms with integral and enum values; ensure header is inert when template-auto support is unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_list_v.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_map_find.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_map_find.hpp

Purpose: Implements lookup of an entry by key in an MP11 map represented as a list of list-like entries.

Important APIs, types, and functions: `mp_map_find<M,K>` and internal `mp_map_find_impl`. GCC 14 workaround paths wrap entries to avoid compiler bug 120161.

Control flow: Normal implementation builds an overload set through inheritance from `mp_identity<T>` for each entry and overload resolution selects the entry whose front element matches `K`; missing keys yield `void`. Workaround path wraps tuples/lists before lookup and unwraps afterward.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Used by `algorithm.hpp` for fallback `mp_at_c` and by MP11 map utilities.

Risks: Map entries must have key as front element. Duplicate keys select according to overload behavior and are not a runtime error. Workaround code is compiler-version sensitive.

Test signals: Static assertions for found/missing keys, tuple/list entries, duplicate-key expectations, and GCC workaround builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_map_find.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_min_element.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_min_element.hpp

Purpose: Implements minimum and maximum element selection over MP11 lists using a comparator predicate.

Important APIs, types, and functions: `mp_min_element<L,P>`, `mp_min_element_q`, `mp_max_element<L,P>`, `mp_max_element_q`, and internal `select_min`/`select_max` fold functors.

Control flow: Starts with `mp_first<L>` and folds over `mp_rest<L>`, replacing the current best when predicate comparison indicates a smaller/larger element.

State and persistence behavior: Compile-time accumulator type only.

Dependencies and integration points: Used by MP11 function utilities and algorithms such as min/max.

Risks: Empty lists are invalid because `mp_first`/`mp_rest` require elements. Comparator must expose boolean `value` and be strict enough for predictable selection.

Test signals: Static assertions for integer constants, custom comparators, quote variants, single-element lists, and compile-fail empty list behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_min_element.hpp -->
