# Research Group subset-b-009678

This grouped report covers vendored Boost.MP11 and Boost.Predef headers under `sources/user-network-fs/mergerfs/vendored/boost`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp

## Purpose

Implements `boost::mp11::mp_plus`, a header-only metafunction that sums the `::value` members of integral-constant types and returns a `std::integral_constant` whose value type follows C++ usual arithmetic conversions. It is a private-detail building block used by higher-level MP11 algorithms that need compile-time arithmetic.

## Important APIs, Types, and Functions

The public alias is `template<class... T> using mp_plus = typename detail::mp_plus_impl<T...>::type`. `detail::mp_plus_impl` has a fold-expression implementation when the compiler supports it and otherwise recursive specializations, including a ten-at-a-time path to reduce template depth. Detected alias templates include `mp_plus`. Implementation structs include `mp_plus_impl`.

## Control Flow

Instantiation selects the fold path or compatibility path from `detail/config.hpp`. The empty pack yields `std::integral_constant<int, 0>`. Non-empty packs accumulate `T::value`, preserving the computed expression type with `decltype` in modern compilers or by recursive addition in older compilers.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

All operands must expose a usable constant `value`; bad inputs fail at template substitution. Signed/unsigned mixing follows C++ conversion rules and can surprise callers. The fallback exists for old GCC/MSVC/Clang behavior, so changes must be tested with the supported compiler matrix.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp

## Purpose

Defines `mp_remove_if` and `mp_remove_if_q`, list filters that remove elements for which a predicate is true. It is a detail header used by set/list algorithms while preserving the input list template.

## Important APIs, Types, and Functions

`mp_remove_if<L, P>` accepts a template predicate and `mp_remove_if_q<L, Q>` accepts a quoted predicate with `Q::template fn`. Internally `_f` maps each element to either an empty `mp_list<>` or singleton `mp_list<T>`, and `mp_append` flattens the kept elements. Detected alias templates include `mp_remove_if`, `mp_remove_if_q`. Implementation structs include `mp_remove_if_impl`, `_f`.

## Control Flow

The implementation specializes only list-like `L<T...>` forms. It transforms each element through `mp_eval_if<P<T>, mp_list<>, mp_list, T>` and appends the resulting small lists back into the original list shape.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/utility.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The predicate must be valid for every element and expose a boolean `::value`. Non-list inputs intentionally produce a missing `type` diagnostic. Since this is type-level filtering, very large packs may still stress template instantiation limits.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp

## Purpose

Provides list-template rebinding and application helpers: `mp_rename`, `mp_apply`, and `mp_apply_q`. These are central MP11 adapters for turning one variadic type-list representation into another or invoking a metafunction over list elements.

## Important APIs, Types, and Functions

`mp_rename<L, B>` rebuilds `L<T...>` as `B<T...>`. `mp_apply<F, L>` applies template `F` to list elements. `mp_apply_q<Q, L>` invokes quoted metafunction `Q::template fn`. When template-auto is enabled it also supports value-list templates by wrapping auto arguments with `mp_value` when applying type metafunctions. Detected alias templates include `mp_rename`, `mp_apply`, `mp_apply_q`. Implementation structs include `mp_rename_impl`.

## Control Flow

Specializations unpack either `template<class...>` or `template<auto...>` lists, then recompose the destination template. `mp_defer` is included to delay invalid applications until selected, which supports SFINAE-friendly higher-level utilities.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/mp_defer.hpp`, `boost/mp11/detail/mp_value.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Input must be a recognized variadic list shape. Value-list support depends on compiler feature macros. Applying a metafunction that rejects the element pack gives compile-time diagnostics at the alias instantiation site.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp

## Purpose

Defines `mp_value`, the MP11 wrapper for non-type template values. It makes `auto` template parameters usable in type-list algorithms by presenting a `std::integral_constant`-like type.

## Important APIs, Types, and Functions

With template-auto support, `template<auto A> using mp_value = std::integral_constant<decltype(A), A>`. On older compilers, the fallback is a small struct template `mp_value<T, A>` inheriting from `std::integral_constant<T, A>`. Detected alias templates include `mp_value`.

## Control Flow

The header is selected by `BOOST_MP11_HAS_TEMPLATE_AUTO`. Higher-level list/value-list adapters use `mp_value<A>` to convert raw non-type arguments into types with `::value` and `value_type`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The public spelling differs across compiler feature sets, so code should consume it through MP11 aliases rather than depending on implementation details. Values must be legal non-type template arguments for the active language mode.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp

## Purpose

Implements `mp_void`, MP11’s equivalent of `void_t`, for SFINAE probes and lazy validity checks.

## Important APIs, Types, and Functions

Modern compilers get `template<class...> using mp_void = void`; old MSVC uses `detail::mp_void_impl<T...>::type` to avoid alias-template substitution bugs. Detected alias templates include `mp_void`. Implementation structs include `mp_void_impl`.

## Control Flow

Callers instantiate `mp_void<Expr...>` in a default template parameter or partial specialization. If all expressions are well-formed the result is `void`; otherwise substitution fails and another overload/specialization can be chosen.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are none. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

It is intentionally minimal. Behavior depends on substitution context; outside SFINAE a bad expression is still a hard compile error. The compatibility branch should not be simplified without old-compiler coverage.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp

## Purpose

Implements `mp_with_index`, a runtime-to-compile-time bridge that calls a function object with an `mp_size_t<I>` corresponding to a runtime index. It supports efficient dispatch over bounded index ranges.

## Important APIs, Types, and Functions

`mp_with_index<N>(i, f)` asserts `i < N` and invokes `f(mp_size_t<I>{})`. Internals provide `detail::mp_with_index_impl<N>::call`, specialized switch tables for many power-of-two and small fixed sizes, plus constexpr/unreachable macros for compiler optimization. Implementation structs include `mp_with_index_impl_`.

## Control Flow

The runtime index is checked, then dispatch enters a generated switch or recursive range split. Each case materializes the chosen index as a type, allowing downstream code to select tuple elements, array slots, or type-list positions at compile time while still receiving the index from runtime input.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`, `utility`, `cassert`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The assertion is the only runtime guard in release builds if assertions are disabled, so callers must respect `i < N`. Large `N` expands substantial switch/template code. Return-type consistency is required across all possible `f(mp_size_t<I>)` calls.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp

## Purpose

Defines MP11 boolean and comparison metafunctions over integral-constant-like types. It supplies logical composition, sameness/similarity checks, signed-safe less-than comparison, and min/max helpers.

## Important APIs, Types, and Functions

Exports `mp_and`, `mp_all`, `mp_or`, `mp_any`, `mp_same`, `mp_similar`, `mp_less`, `mp_min`, and `mp_max`. Implementations use `mp_void`, `mp_count`, `mp_count_if`, `mp_min_element`, `mp_plus`, and lazy `mp_eval_if` utilities. Detected alias templates include `mp_and`, `mp_and`, `mp_all`, `mp_all`, `mp_or`, `mp_any`, `mp_any`, `mp_same`, `mp_similar`, `mp_less`, `mp_min`, `mp_max`. Implementation structs include `mp_and_impl`, `mp_or_impl`, `mp_same_impl`, `mp_similar_impl`.

## Control Flow

`mp_and` and `mp_or` short-circuit through lazy evaluation where needed; `mp_all`/`mp_any` compute aggregate truth over packs. `mp_same` counts exact type matches, `mp_similar` checks matching outer templates, and `mp_less` avoids signed/unsigned warning-prone direct comparisons. `mp_min`/`mp_max` delegate to min/max-element over an `mp_list`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/utility.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_count.hpp`, `boost/mp11/detail/mp_plus.hpp`, `boost/mp11/detail/mp_min_element.hpp`, `boost/mp11/detail/mp_void.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Inputs are expected to expose `::value` convertible to bool or comparable numeric values. The file carries compiler workarounds for MSVC and GCC bugs; replacing them with simpler pack expressions can regress old supported compilers.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp

## Purpose

Provides MP11’s C++11-compatible implementation of `integer_sequence`, `index_sequence`, and sequence-generation aliases, with compiler-intrinsic fast paths when available.

## Important APIs, Types, and Functions

Defines `integer_sequence<T, I...>`, `make_integer_sequence<T, N>`, `index_sequence`, `make_index_sequence<N>`, and `index_sequence_for<T...>`. It can use `__make_integer_seq` where available, otherwise builds sequences by recursive splitting and append. Detected alias templates include `make_integer_sequence`, `iseq_if_c`, `make_integer_sequence`, `index_sequence`, `make_index_sequence`, `index_sequence_for`. Implementation structs include `integer_sequence`, `iseq_if_c_impl`, `iseq_identity`, `append_integer_sequence`, `make_integer_sequence_impl`, `make_integer_sequence_impl_`.

## Control Flow

For generated sequences the fallback recursively halves `N`, creates smaller sequences, appends them with shifted values, and conditionally adds the final odd element. Negative `N` resolves to a missing type through `iseq_if_c`, producing a compile-time error.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/version.hpp`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Large sequence generation can be template-heavy without compiler intrinsics. `N` must be non-negative and fit the selected integral type. The implementation is low-level infrastructure for tuple/list algorithms, so off-by-one errors would cascade broadly.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp

## Purpose

Defines common MP11 integral constants and boolean adapters used throughout the library.

## Important APIs, Types, and Functions

Exports `mp_bool<B>`, `mp_true`, `mp_false`, `mp_to_bool<T>`, `mp_not<T>`, `mp_int<I>`, `mp_size_t<N>`, and includes `mp_value` for non-type value wrappers. Detected alias templates include `mp_bool`, `mp_to_bool`, `mp_not`, `mp_int`, `mp_size_t`.

## Control Flow

The aliases map directly to `std::integral_constant` forms. Higher-level metafunctions use these stable names instead of repeating standard-library spellings and to normalize arbitrary `T::value` constants to bool.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/version.hpp`, `boost/mp11/detail/mp_value.hpp`, `type_traits`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

This header has no runtime behavior, but all consumers assume `::value` exists and is constant-expression friendly. Compile errors here usually indicate a non-integral-constant input passed into MP11 logic.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp

## Purpose

Defines MP11 list manipulation primitives for type lists and, where supported, value lists. It is the main public header for list size, rebinding, element access, push/pop, replacement, and element transformation.

## Important APIs, Types, and Functions

Exports `mp_list_c`, `mp_size`, `mp_empty`, `mp_assign`, `mp_clear`, `mp_pop_front`, `mp_first`, `mp_rest`, `mp_second`, `mp_third`, `mp_push_front`, `mp_push_back`, `mp_rename_v`, `mp_replace_front/first/second/third`, and `mp_transform_front/first/second/third` plus `_q` quoted variants. Detected alias templates include `mp_list_c`, `mp_size`, `mp_empty`, `mp_assign`, `mp_clear`, `mp_pop_front`, `mp_first`, `mp_rest`, `mp_second`, `mp_third`, `mp_push_front`, `mp_push_back`, `mp_rename_v`, `mp_replace_front`, `mp_replace_first`, `mp_replace_second`, `mp_replace_third`, `mp_transform_front`. Implementation structs include `mp_size_impl`, `mp_assign_impl`, `mp_pop_front_impl`, `mp_second_impl`, `mp_third_impl`, `mp_push_front_impl`, `mp_push_back_impl`, `mp_rename_v_impl`, `mp_replace_front_impl`, `mp_replace_second_impl`.

## Control Flow

Most operations partially specialize on `L<T...>` and rebuild the same outer template with modified element packs. Template-auto branches support `L<A...>` value lists by converting between raw values and `mp_value` wrappers. Diagnostics are intentionally expressed as missing `type` when an input is not a list or is too short.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_list_v.hpp`, `boost/mp11/detail/mp_is_list.hpp`, `boost/mp11/detail/mp_is_value_list.hpp`, `boost/mp11/detail/mp_front.hpp`, `boost/mp11/detail/mp_rename.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Operations preserve the original outer template, which is useful but can surprise when the target container has constraints. Empty or too-short lists fail at compile time. The temporary push/pop of macro `I` protects against platform headers that define `I` as a macro.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp

## Purpose

Implements set-like algorithms over MP11 type lists, treating type identity as membership and preserving list order where possible.

## Important APIs, Types, and Functions

Exports `mp_set_contains`, `mp_set_push_back`, `mp_set_push_front`, `mp_is_set`, `mp_set_union`, `mp_set_intersection`, and `mp_set_difference`. It uses `mp_inherit<mp_identity<T>...>` for efficient membership, plus fold/copy/remove helpers. Detected alias templates include `mp_set_contains`, `mp_set_push_back`, `mp_set_push_front`, `mp_is_set`, `mp_set_union_`, `mp_set_union`, `mp_set_intersection_`, `mp_set_intersection`, `mp_set_difference`. Implementation structs include `mp_set_contains_impl`, `mp_set_push_back_impl`, `mp_set_push_front_impl`, `mp_is_set_helper_start`, `mp_is_set_helper`, `mp_is_set_impl`, `mp_set_union_impl`, `in_all_sets`, `mp_set_intersection_impl`, `in_any_set`.

## Control Flow

Membership is tested through base-class lookup. Push operations add only absent types. `mp_is_set` folds through the pack to detect duplicates. Union appends missing elements from later lists; intersection copies elements present in all other sets; difference removes elements present in any excluded set.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/utility.hpp`, `boost/mp11/function.hpp`, `boost/mp11/detail/config.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/mp_copy_if.hpp`, `boost/mp11/detail/mp_fold.hpp`, `boost/mp11/detail/mp_remove_if.hpp`, `boost/mp11/detail/mp_is_list.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

These are type-identity sets, not value or trait equivalence sets. Duplicate handling is deterministic but template-heavy on very large packs. Non-list operands trigger substitution failures through `mp_is_list` gates or missing implementation `type`s.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp

## Purpose

Adds runtime tuple algorithms that use MP11 integer sequences: apply a callable to tuple elements, construct an object from a tuple, iterate a tuple, and transform one or more tuple-like objects element-wise.

## Important APIs, Types, and Functions

Exports `tuple_apply`, `construct_from_tuple`, `tuple_for_each`, and `tuple_transform`. It uses unqualified `get` via `using std::get` so tuple-like types can participate through ADL, and derives index ranges from `std::tuple_size`.

## Control Flow

Each algorithm builds a `make_index_sequence` for the tuple length. `tuple_apply` expands `get<J>(tp)...` into the callable. `construct_from_tuple` forwards elements into `T(...)`. `tuple_for_each` uses an initializer-list expansion for ordered side effects. `tuple_transform` groups same-index elements across all input tuples and returns a new `std::tuple` of results.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integer_sequence.hpp`, `boost/mp11/list.hpp`, `boost/mp11/function.hpp`, `boost/mp11/detail/config.hpp`, `tuple`, `utility`, `type_traits`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

All tuple inputs to `tuple_transform` must have the same length. Result/value categories are encoded through forwarding helper tuples, so dangling references are possible if callers store tuples of references beyond source lifetimes. Old MSVC branches limit variadic transform behavior.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp

## Purpose

Provides MP11 utility metafunctions for identity, inheritance aggregation, lazy conditional evaluation, validity probing, quoted metafunctions, negation, and composition.

## Important APIs, Types, and Functions

Exports `mp_identity`, `mp_identity_t`, `mp_inherit`, `mp_eval_if_c`, `mp_eval_if`, `mp_eval_if_q`, `mp_eval_if_not`, `mp_eval_or`, `mp_valid_and_true`, `mp_cond`, `mp_quote`, `mp_quote_trait`, `mp_invoke_q`, `mp_not_fn`, `mp_not_fn_q`, `mp_compose`, and `mp_compose_q`. Detected alias templates include `mp_identity_t`, `mp_eval_if_c`, `mp_eval_if`, `mp_eval_if_q`, `mp_eval_if_not`, `mp_eval_if_not_q`, `mp_eval_or`, `mp_eval_or_q`, `mp_valid_and_true`, `mp_valid_and_true_q`, `mp_cond`, `mp_cond_`, `mp_invoke_q`, `mp_invoke_q`, `mp_invoke_q`, `mp_not_fn_q`, `mp_compose_helper`. Implementation structs include `mp_identity`, `mp_inherit`, `mp_eval_if_c_impl`, `mp_cond_impl`, `mp_quote`, `mp_quote_trait`, `mp_invoke_q_impl`, `mp_not_fn`, `mp_compose`, `mp_compose_q`.

## Control Flow

Lazy helpers select either an already-formed type or a deferred metafunction instantiation, preventing invalid branches from being instantiated. Quote helpers adapt templates and traits into uniform `Q::template fn` objects. Composition folds intermediate results through lists and applies quoted functions from right to left.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_fold.hpp`, `boost/mp11/detail/mp_front.hpp`, `boost/mp11/detail/mp_rename.hpp`, `boost/mp11/detail/mp_defer.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The utilities are SFINAE-sensitive; moving eager instantiations into lazy paths or vice versa changes compile-time failure behavior. Composition and conditional helpers rely on list/application primitives, so invalid quoted functions surface as template diagnostics.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp

## Purpose

Declares the vendored Boost.MP11 version macro.

## Important APIs, Types, and Functions

Defines `BOOST_MP11_VERSION` as `109000`, representing the MP11 version encoded as a single integer.

## Control Flow

Including the header simply makes the macro available to conditional code and to other MP11 headers such as `integer_sequence.hpp` and `integral.hpp`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are none. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

There is no runtime behavior. The risk is version skew if vendored headers are updated incompletely while this macro remains stale.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef.h` is a umbrella Boost.Predef include for related detection headers. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/language.h`, `boost/predef/architecture.h`, `boost/predef/compiler.h`, `boost/predef/library.h`, `boost/predef/os.h`, `boost/predef/other.h`, `boost/predef/platform.h`, `boost/predef/hardware.h`, `boost/predef/version.h`. Consumers normally include this file when they want the whole `sources/user-network-fs/mergerfs/vendored/boost/predef.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h` is a umbrella architecture include that gathers all CPU architecture predefs and exposes their available/version macros to callers. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/architecture/alpha.h`, `boost/predef/architecture/arm.h`, `boost/predef/architecture/blackfin.h`, `boost/predef/architecture/convex.h`, `boost/predef/architecture/e2k.h`, `boost/predef/architecture/ia64.h`, `boost/predef/architecture/loongarch.h`, `boost/predef/architecture/m68k.h`, `boost/predef/architecture/mips.h`, `boost/predef/architecture/parisc.h`, `boost/predef/architecture/ppc.h`, `boost/predef/architecture/ptx.h`, `boost/predef/architecture/pyramid.h`, `boost/predef/architecture/riscv.h`, `boost/predef/architecture/rs6k.h`, `boost/predef/architecture/sparc.h`, `boost/predef/architecture/superh.h`, `boost/predef/architecture/sys370.h`, `boost/predef/architecture/sys390.h`, `boost/predef/architecture/x86.h`, `boost/predef/architecture/z.h`. Consumers normally include this file when they want the whole `architecture.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/alpha.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/alpha.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/alpha.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_ALPHA`. Other relevant macros in this header include `BOOST_ARCH_ALPHA`, `BOOST_ARCH_ALPHA_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_ALPHA_NAME`. Display-name macros are `BOOST_ARCH_ALPHA_NAME` "DEC Alpha". Predef test registrations are `BOOST_ARCH_ALPHA,BOOST_ARCH_ALPHA_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__alpha__`, `__alpha`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/alpha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/arm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/arm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/arm.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_ARM`. Other relevant macros in this header include `BOOST_ARCH_ARM`, `BOOST_ARCH_ARM_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_ARM_NAME`. Display-name macros are `BOOST_ARCH_ARM_NAME` "ARM". Predef test registrations are `BOOST_ARCH_ARM,BOOST_ARCH_ARM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/blackfin.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/blackfin.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/blackfin.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_BLACKFIN`. Other relevant macros in this header include `BOOST_ARCH_BLACKFIN`, `BOOST_ARCH_BLACKFIN_AVAILABLE`, `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_BLACKFIN_NAME`. Display-name macros are `BOOST_ARCH_BLACKFIN_NAME` "Blackfin". Predef test registrations are `BOOST_ARCH_BLACKFIN,BOOST_ARCH_BLACKFIN_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__bfin__`, `__BFIN__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/blackfin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/convex.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/convex.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/convex.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_CONVEX`. Other relevant macros in this header include `BOOST_ARCH_CONVEX`, `BOOST_ARCH_CONVEX_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_CONVEX_NAME`. Display-name macros are `BOOST_ARCH_CONVEX_NAME` "Convex Computer". Predef test registrations are `BOOST_ARCH_CONVEX,BOOST_ARCH_CONVEX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__convex__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/convex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/e2k.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/e2k.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/e2k.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_E2K`. Other relevant macros in this header include `BOOST_ARCH_E2K`, `BOOST_ARCH_E2K_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_E2K_NAME`. Display-name macros are `BOOST_ARCH_E2K_NAME` "E2K". Predef test registrations are `BOOST_ARCH_E2K,BOOST_ARCH_E2K_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__e2k__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/e2k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ia64.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ia64.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ia64.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_IA64`. Other relevant macros in this header include `BOOST_ARCH_IA64`, `BOOST_ARCH_IA64_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_IA64_NAME`. Display-name macros are `BOOST_ARCH_IA64_NAME` "Intel Itanium 64". Predef test registrations are `BOOST_ARCH_IA64,BOOST_ARCH_IA64_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__ia64__`, `_IA64`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ia64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/loongarch.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/loongarch.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/loongarch.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_LOONGARCH`. Other relevant macros in this header include `BOOST_ARCH_LOONGARCH`, `BOOST_ARCH_LOONGARCH_AVAILABLE`, `BOOST_ARCH_LOONGARCH_NAME`. Display-name macros are `BOOST_ARCH_LOONGARCH_NAME` "LoongArch". Predef test registrations are `BOOST_ARCH_LOONGARCH,BOOST_ARCH_LOONGARCH_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__loongarch__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/loongarch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/m68k.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/m68k.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/m68k.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_M68K`. Other relevant macros in this header include `BOOST_ARCH_M68K`, `BOOST_ARCH_M68K_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_M68K_NAME`. Display-name macros are `BOOST_ARCH_M68K_NAME` "Motorola 68k". Predef test registrations are `BOOST_ARCH_M68K,BOOST_ARCH_M68K_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__m68k__`, `M68000`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/m68k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/mips.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/mips.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/mips.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_MIPS`. Other relevant macros in this header include `BOOST_ARCH_MIPS`, `BOOST_ARCH_MIPS_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_MIPS_NAME`. Display-name macros are `BOOST_ARCH_MIPS_NAME` "MIPS". Predef test registrations are `BOOST_ARCH_MIPS,BOOST_ARCH_MIPS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__mips__`, `__mips`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/parisc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/parisc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/parisc.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_PARISC`. Other relevant macros in this header include `BOOST_ARCH_PARISC`, `BOOST_ARCH_PARISC_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_PARISC_NAME`. Display-name macros are `BOOST_ARCH_PARISC_NAME` "HP/PA RISC". Predef test registrations are `BOOST_ARCH_PARISC,BOOST_ARCH_PARISC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__hppa__`, `__hppa`, `__HPPA__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/parisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ppc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ppc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ppc.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_PPC`, `BOOST_ARCH_PPC_64`. Other relevant macros in this header include `BOOST_ARCH_PPC`, `BOOST_ARCH_PPC_AVAILABLE`, `BOOST_ARCH_PPC_NAME`, `BOOST_ARCH_PPC_64`, `BOOST_ARCH_PPC_64_AVAILABLE`, `BOOST_ARCH_PPC_64_NAME`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`. Display-name macros are `BOOST_ARCH_PPC_NAME` "PowerPC", `BOOST_ARCH_PPC_64_NAME` "PowerPC64". Predef test registrations are `BOOST_ARCH_PPC,BOOST_ARCH_PPC_NAME`, `BOOST_ARCH_PPC_64,BOOST_ARCH_PPC_64_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__powerpc`, `__powerpc__`, `__powerpc64__`, `__ppc64__`, `__PPC64__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ptx.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ptx.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ptx.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_PTX`. Other relevant macros in this header include `BOOST_ARCH_PTX`, `BOOST_ARCH_PTX_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_PTX_NAME`. Display-name macros are `BOOST_ARCH_PTX_NAME` "PTX". Predef test registrations are `BOOST_ARCH_PTX,BOOST_ARCH_PTX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__CUDA_ARCH__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/ptx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/pyramid.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/pyramid.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/pyramid.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_PYRAMID`. Other relevant macros in this header include `BOOST_ARCH_PYRAMID`, `BOOST_ARCH_PYRAMID_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_PYRAMID_NAME`. Display-name macros are `BOOST_ARCH_PYRAMID_NAME` "Pyramid 9810". Predef test registrations are `BOOST_ARCH_PYRAMID,BOOST_ARCH_PYRAMID_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `pyr`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/pyramid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/riscv.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/riscv.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/riscv.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_RISCV`. Other relevant macros in this header include `BOOST_ARCH_RISCV`, `BOOST_ARCH_RISCV_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_RISCV_NAME`. Display-name macros are `BOOST_ARCH_RISCV_NAME` "RISC-V". Predef test registrations are `BOOST_ARCH_RISCV,BOOST_ARCH_RISCV_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__riscv`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/rs6k.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/rs6k.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/rs6k.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_RS6000`, `BOOST_ARCH_PWR`. Other relevant macros in this header include `BOOST_ARCH_RS6000`, `BOOST_ARCH_RS6000_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_RS6000_NAME`, `BOOST_ARCH_PWR`, `BOOST_ARCH_PWR_AVAILABLE`, `BOOST_ARCH_PWR_NAME`. Display-name macros are `BOOST_ARCH_RS6000_NAME` "RS/6000", `BOOST_ARCH_PWR_NAME` BOOST_ARCH_RS6000_NAME. Predef test registrations are `BOOST_ARCH_RS6000,BOOST_ARCH_RS6000_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__THW_RS6000`, `_IBMR2`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/rs6k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sparc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sparc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sparc.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_SPARC`. Other relevant macros in this header include `BOOST_ARCH_SPARC`, `BOOST_ARCH_SPARC_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_SPARC_NAME`. Display-name macros are `BOOST_ARCH_SPARC_NAME` "SPARC". Predef test registrations are `BOOST_ARCH_SPARC,BOOST_ARCH_SPARC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__sparc__`, `__sparc`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sparc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/superh.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/superh.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/superh.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_SH`. Other relevant macros in this header include `BOOST_ARCH_SH`, `BOOST_ARCH_SH_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_SH_NAME`. Display-name macros are `BOOST_ARCH_SH_NAME` "SuperH". Predef test registrations are `BOOST_ARCH_SH,BOOST_ARCH_SH_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__sh__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/superh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys370.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys370.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys370.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_SYS370`. Other relevant macros in this header include `BOOST_ARCH_SYS370`, `BOOST_ARCH_SYS370_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_SYS370_NAME`. Display-name macros are `BOOST_ARCH_SYS370_NAME` "System/370". Predef test registrations are `BOOST_ARCH_SYS370,BOOST_ARCH_SYS370_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__370__`, `__THW_370__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys370.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys390.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys390.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys390.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_SYS390`. Other relevant macros in this header include `BOOST_ARCH_SYS390`, `BOOST_ARCH_SYS390_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_SYS390_NAME`. Display-name macros are `BOOST_ARCH_SYS390_NAME` "System/390". Predef test registrations are `BOOST_ARCH_SYS390,BOOST_ARCH_SYS390_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__s390__`, `__s390x__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/sys390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_X86`. Other relevant macros in this header include `BOOST_ARCH_X86`, `BOOST_ARCH_X86_AVAILABLE`, `BOOST_ARCH_X86_NAME`. Display-name macros are `BOOST_ARCH_X86_NAME` "Intel x86". Predef test registrations are `BOOST_ARCH_X86,BOOST_ARCH_X86_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/architecture/x86/32.h`, `boost/predef/architecture/x86/64.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/32.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/32.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/32.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_X86_32`. Other relevant macros in this header include `BOOST_ARCH_X86_32`, `BOOST_ARCH_X86_32_AVAILABLE`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_X86_32_NAME`. Display-name macros are `BOOST_ARCH_X86_32_NAME` "Intel x86-32". Predef test registrations are `BOOST_ARCH_X86_32,BOOST_ARCH_X86_32_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `i386`, `__i386__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/architecture/x86.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/64.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/64.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/64.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_X86_64`. Other relevant macros in this header include `BOOST_ARCH_X86_64`, `BOOST_ARCH_X86_64_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_X86_64_NAME`. Display-name macros are `BOOST_ARCH_X86_64_NAME` "Intel x86-64". Predef test registrations are `BOOST_ARCH_X86_64,BOOST_ARCH_X86_64_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__x86_64`, `__x86_64__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/architecture/x86.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/x86/64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/z.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/z.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/z.h` is a Boost.Predef architecture detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_ARCH_Z`. Other relevant macros in this header include `BOOST_ARCH_Z`, `BOOST_ARCH_Z_AVAILABLE`, `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_Z_NAME`. Display-name macros are `BOOST_ARCH_Z_NAME` "z/Architecture". Predef test registrations are `BOOST_ARCH_Z,BOOST_ARCH_Z_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__SYSC_ZARCH__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Architecture detectors may additionally define `BOOST_ARCH_WORD_BITS_16`, `BOOST_ARCH_WORD_BITS_32`, or `BOOST_ARCH_WORD_BITS_64` based on the detected architecture level.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/architecture/z.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h` is a umbrella compiler include that detects known compiler front ends and emulated compilers in a precedence-sensitive order. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/compiler/borland.h`, `boost/predef/compiler/clang.h`, `boost/predef/compiler/comeau.h`, `boost/predef/compiler/compaq.h`, `boost/predef/compiler/diab.h`, `boost/predef/compiler/digitalmars.h`, `boost/predef/compiler/dignus.h`, `boost/predef/compiler/edg.h`, `boost/predef/compiler/ekopath.h`, `boost/predef/compiler/gcc_xml.h`, `boost/predef/compiler/gcc.h`, `boost/predef/compiler/greenhills.h`, `boost/predef/compiler/hp_acc.h`, `boost/predef/compiler/iar.h`, `boost/predef/compiler/ibm.h`, `boost/predef/compiler/intel.h`, `boost/predef/compiler/kai.h`, `boost/predef/compiler/llvm.h`, `boost/predef/compiler/metaware.h`, `boost/predef/compiler/metrowerks.h`, `boost/predef/compiler/microtec.h`, `boost/predef/compiler/mpw.h`, `boost/predef/compiler/nvcc.h`, `boost/predef/compiler/palm.h`, `boost/predef/compiler/pgi.h`, `boost/predef/compiler/sgi_mipspro.h`, `boost/predef/compiler/sunpro.h`, `boost/predef/compiler/tendra.h`, `boost/predef/compiler/visualc.h`, `boost/predef/compiler/watcom.h`. Consumers normally include this file when they want the whole `compiler.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/borland.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/borland.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/borland.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_BORLAND`, `BOOST_COMP_BORLAND_DETECTION`, `BOOST_COMP_BORLAND_EMULATED`. Other relevant macros in this header include `BOOST_COMP_BORLAND`, `BOOST_COMP_BORLAND_DETECTION`, `BOOST_COMP_BORLAND_AVAILABLE`, `BOOST_COMP_BORLAND_EMULATED`, `BOOST_COMP_BORLAND_NAME`. Display-name macros are `BOOST_COMP_BORLAND_NAME` "Borland C++". Predef test registrations are `BOOST_COMP_BORLAND,BOOST_COMP_BORLAND_NAME`, `BOOST_COMP_BORLAND_EMULATED,BOOST_COMP_BORLAND_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__BORLANDC__`, `__CODEGEARC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/borland.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/clang.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/clang.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/clang.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_CLANG`, `BOOST_COMP_CLANG_DETECTION`, `BOOST_COMP_CLANG_EMULATED`. Other relevant macros in this header include `BOOST_COMP_CLANG`, `BOOST_COMP_CLANG_DETECTION`, `BOOST_COMP_CLANG_EMULATED`, `BOOST_COMP_CLANG_AVAILABLE`, `BOOST_COMP_CLANG_NAME`. Display-name macros are `BOOST_COMP_CLANG_NAME` "Clang". Predef test registrations are `BOOST_COMP_CLANG,BOOST_COMP_CLANG_NAME`, `BOOST_COMP_CLANG_EMULATED,BOOST_COMP_CLANG_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__clang__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/clang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/comeau.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/comeau.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/comeau.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_COMO`, `BOOST_COMP_COMO_DETECTION`, `BOOST_COMP_COMO_EMULATED`. Other relevant macros in this header include `BOOST_COMP_COMO`, `BOOST_COMP_COMO_DETECTION`, `BOOST_COMP_COMO_EMULATED`, `BOOST_COMP_COMO_AVAILABLE`, `BOOST_COMP_COMO_NAME`. Display-name macros are `BOOST_COMP_COMO_NAME` "Comeau C++". Predef test registrations are `BOOST_COMP_COMO,BOOST_COMP_COMO_NAME`, `BOOST_COMP_COMO_EMULATED,BOOST_COMP_COMO_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__COMO__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/comeau.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/compaq.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/compaq.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/compaq.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_DEC`, `BOOST_COMP_DEC_DETECTION`, `BOOST_COMP_DEC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_DEC`, `BOOST_COMP_DEC_DETECTION`, `BOOST_COMP_DEC_EMULATED`, `BOOST_COMP_DEC_AVAILABLE`, `BOOST_COMP_DEC_NAME`. Display-name macros are `BOOST_COMP_DEC_NAME` "Compaq C/C++". Predef test registrations are `BOOST_COMP_DEC,BOOST_COMP_DEC_NAME`, `BOOST_COMP_DEC_EMULATED,BOOST_COMP_DEC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__DECC`, `__DECCXX`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/compaq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/diab.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/diab.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/diab.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_DIAB`, `BOOST_COMP_DIAB_DETECTION`, `BOOST_COMP_DIAB_EMULATED`. Other relevant macros in this header include `BOOST_COMP_DIAB`, `BOOST_COMP_DIAB_DETECTION`, `BOOST_COMP_DIAB_EMULATED`, `BOOST_COMP_DIAB_AVAILABLE`, `BOOST_COMP_DIAB_NAME`. Display-name macros are `BOOST_COMP_DIAB_NAME` "Diab C/C++". Predef test registrations are `BOOST_COMP_DIAB,BOOST_COMP_DIAB_NAME`, `BOOST_COMP_DIAB_EMULATED,BOOST_COMP_DIAB_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__DCC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/diab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/digitalmars.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/digitalmars.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/digitalmars.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_DMC`, `BOOST_COMP_DMC_DETECTION`, `BOOST_COMP_DMC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_DMC`, `BOOST_COMP_DMC_DETECTION`, `BOOST_COMP_DMC_EMULATED`, `BOOST_COMP_DMC_AVAILABLE`, `BOOST_COMP_DMC_NAME`. Display-name macros are `BOOST_COMP_DMC_NAME` "Digital Mars". Predef test registrations are `BOOST_COMP_DMC,BOOST_COMP_DMC_NAME`, `BOOST_COMP_DMC_EMULATED,BOOST_COMP_DMC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__DMC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/digitalmars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/dignus.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/dignus.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/dignus.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_SYSC`, `BOOST_COMP_SYSC_DETECTION`, `BOOST_COMP_SYSC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_SYSC`, `BOOST_COMP_SYSC_DETECTION`, `BOOST_COMP_SYSC_EMULATED`, `BOOST_COMP_SYSC_AVAILABLE`, `BOOST_COMP_SYSC_NAME`. Display-name macros are `BOOST_COMP_SYSC_NAME` "Dignus Systems/C++". Predef test registrations are `BOOST_COMP_SYSC,BOOST_COMP_SYSC_NAME`, `BOOST_COMP_SYSC_EMULATED,BOOST_COMP_SYSC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__SYSC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/dignus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/edg.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/edg.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/edg.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_EDG`, `BOOST_COMP_EDG_DETECTION`, `BOOST_COMP_EDG_EMULATED`. Other relevant macros in this header include `BOOST_COMP_EDG`, `BOOST_COMP_EDG_DETECTION`, `BOOST_COMP_EDG_EMULATED`, `BOOST_COMP_EDG_AVAILABLE`, `BOOST_COMP_EDG_NAME`. Display-name macros are `BOOST_COMP_EDG_NAME` "EDG C++ Frontend". Predef test registrations are `BOOST_COMP_EDG,BOOST_COMP_EDG_NAME`, `BOOST_COMP_EDG_EMULATED,BOOST_COMP_EDG_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__EDG__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/edg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ekopath.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ekopath.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ekopath.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_PATH`, `BOOST_COMP_PATH_DETECTION`, `BOOST_COMP_PATH_EMULATED`. Other relevant macros in this header include `BOOST_COMP_PATH`, `BOOST_COMP_PATH_DETECTION`, `BOOST_COMP_PATH_EMULATED`, `BOOST_COMP_PATH_AVAILABLE`, `BOOST_COMP_PATH_NAME`. Display-name macros are `BOOST_COMP_PATH_NAME` "EKOpath". Predef test registrations are `BOOST_COMP_PATH,BOOST_COMP_PATH_NAME`, `BOOST_COMP_PATH_EMULATED,BOOST_COMP_PATH_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__PATHCC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ekopath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_GNUC`, `BOOST_COMP_GNUC_DETECTION`, `BOOST_COMP_GNUC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_GNUC`, `BOOST_COMP_GNUC_DETECTION`, `BOOST_COMP_GNUC_EMULATED`, `BOOST_COMP_GNUC_AVAILABLE`, `BOOST_COMP_GNUC_NAME`. Display-name macros are `BOOST_COMP_GNUC_NAME` "Gnu GCC C/C++". Predef test registrations are `BOOST_COMP_GNUC,BOOST_COMP_GNUC_NAME`, `BOOST_COMP_GNUC_EMULATED,BOOST_COMP_GNUC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__GNUC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/compiler/clang.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc_xml.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc_xml.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc_xml.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_GCCXML`, `BOOST_COMP_GCCXML_DETECTION`, `BOOST_COMP_GCCXML_EMULATED`. Other relevant macros in this header include `BOOST_COMP_GCCXML`, `BOOST_COMP_GCCXML_DETECTION`, `BOOST_COMP_GCCXML_EMULATED`, `BOOST_COMP_GCCXML_AVAILABLE`, `BOOST_COMP_GCCXML_NAME`. Display-name macros are `BOOST_COMP_GCCXML_NAME` "GCC XML". Predef test registrations are `BOOST_COMP_GCCXML,BOOST_COMP_GCCXML_NAME`, `BOOST_COMP_GCCXML_EMULATED,BOOST_COMP_GCCXML_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__GCCXML__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/gcc_xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/greenhills.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/greenhills.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/greenhills.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_GHS`, `BOOST_COMP_GHS_DETECTION`, `BOOST_COMP_GHS_EMULATED`. Other relevant macros in this header include `BOOST_COMP_GHS`, `BOOST_COMP_GHS_DETECTION`, `BOOST_COMP_GHS_EMULATED`, `BOOST_COMP_GHS_AVAILABLE`, `BOOST_COMP_GHS_NAME`. Display-name macros are `BOOST_COMP_GHS_NAME` "Green Hills C/C++". Predef test registrations are `BOOST_COMP_GHS,BOOST_COMP_GHS_NAME`, `BOOST_COMP_GHS_EMULATED,BOOST_COMP_GHS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__ghs`, `__ghs__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/greenhills.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/hp_acc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/hp_acc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/hp_acc.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_HPACC`, `BOOST_COMP_HPACC_DETECTION`, `BOOST_COMP_HPACC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_HPACC`, `BOOST_COMP_HPACC_DETECTION`, `BOOST_COMP_HPACC_EMULATED`, `BOOST_COMP_HPACC_AVAILABLE`, `BOOST_COMP_HPACC_NAME`. Display-name macros are `BOOST_COMP_HPACC_NAME` "HP aC++". Predef test registrations are `BOOST_COMP_HPACC,BOOST_COMP_HPACC_NAME`, `BOOST_COMP_HPACC_EMULATED,BOOST_COMP_HPACC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__HP_aCC`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/hp_acc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/iar.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/iar.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/iar.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_IAR`, `BOOST_COMP_IAR_DETECTION`, `BOOST_COMP_IAR_EMULATED`. Other relevant macros in this header include `BOOST_COMP_IAR`, `BOOST_COMP_IAR_DETECTION`, `BOOST_COMP_IAR_EMULATED`, `BOOST_COMP_IAR_AVAILABLE`, `BOOST_COMP_IAR_NAME`. Display-name macros are `BOOST_COMP_IAR_NAME` "IAR C/C++". Predef test registrations are `BOOST_COMP_IAR,BOOST_COMP_IAR_NAME`, `BOOST_COMP_IAR_EMULATED,BOOST_COMP_IAR_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__IAR_SYSTEMS_ICC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/iar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ibm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ibm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ibm.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_IBM`, `BOOST_COMP_IBM_DETECTION`, `BOOST_COMP_IBM_EMULATED`. Other relevant macros in this header include `BOOST_COMP_IBM`, `BOOST_COMP_IBM_DETECTION`, `BOOST_COMP_IBM_EMULATED`, `BOOST_COMP_IBM_AVAILABLE`, `BOOST_COMP_IBM_NAME`. Display-name macros are `BOOST_COMP_IBM_NAME` "IBM XL C/C++". Predef test registrations are `BOOST_COMP_IBM,BOOST_COMP_IBM_NAME`, `BOOST_COMP_IBM_EMULATED,BOOST_COMP_IBM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__IBMCPP__`, `__xlC__`, `__xlc__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/ibm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/intel.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/intel.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/intel.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_INTEL`, `BOOST_COMP_INTEL_DETECTION`, `BOOST_COMP_INTEL_EMULATED`. Other relevant macros in this header include `BOOST_COMP_INTEL`, `BOOST_COMP_INTEL_DETECTION`, `BOOST_COMP_INTEL_EMULATED`, `BOOST_COMP_INTEL_AVAILABLE`, `BOOST_COMP_INTEL_NAME`. Display-name macros are `BOOST_COMP_INTEL_NAME` "Intel C/C++". Predef test registrations are `BOOST_COMP_INTEL,BOOST_COMP_INTEL_NAME`, `BOOST_COMP_INTEL_EMULATED,BOOST_COMP_INTEL_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__INTEL_COMPILER`, `__ICL`, `__ICC`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/kai.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/kai.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/kai.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_KCC`, `BOOST_COMP_KCC_DETECTION`, `BOOST_COMP_KCC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_KCC`, `BOOST_COMP_KCC_DETECTION`, `BOOST_COMP_KCC_EMULATED`, `BOOST_COMP_KCC_AVAILABLE`, `BOOST_COMP_KCC_NAME`. Display-name macros are `BOOST_COMP_KCC_NAME` "Kai C++". Predef test registrations are `BOOST_COMP_KCC,BOOST_COMP_KCC_NAME`, `BOOST_COMP_KCC_EMULATED,BOOST_COMP_KCC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__KCC`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/kai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/llvm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/llvm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/llvm.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_LLVM`, `BOOST_COMP_LLVM_DETECTION`, `BOOST_COMP_LLVM_EMULATED`. Other relevant macros in this header include `BOOST_COMP_LLVM`, `BOOST_COMP_LLVM_DETECTION`, `BOOST_COMP_LLVM_EMULATED`, `BOOST_COMP_LLVM_AVAILABLE`, `BOOST_COMP_LLVM_NAME`. Display-name macros are `BOOST_COMP_LLVM_NAME` "LLVM". Predef test registrations are `BOOST_COMP_LLVM,BOOST_COMP_LLVM_NAME`, `BOOST_COMP_LLVM_EMULATED,BOOST_COMP_LLVM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__llvm__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/compiler/clang.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/llvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metaware.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metaware.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metaware.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_HIGHC`, `BOOST_COMP_HIGHC_DETECTION`, `BOOST_COMP_HIGHC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_HIGHC`, `BOOST_COMP_HIGHC_DETECTION`, `BOOST_COMP_HIGHC_EMULATED`, `BOOST_COMP_HIGHC_AVAILABLE`, `BOOST_COMP_HIGHC_NAME`. Display-name macros are `BOOST_COMP_HIGHC_NAME` "MetaWare High C/C++". Predef test registrations are `BOOST_COMP_HIGHC,BOOST_COMP_HIGHC_NAME`, `BOOST_COMP_HIGHC_EMULATED,BOOST_COMP_HIGHC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__HIGHC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metaware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metrowerks.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metrowerks.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metrowerks.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_MWERKS`, `BOOST_COMP_MWERKS_DETECTION`, `BOOST_COMP_MWERKS_EMULATED`. Other relevant macros in this header include `BOOST_COMP_MWERKS`, `BOOST_COMP_MWERKS_DETECTION`, `BOOST_COMP_MWERKS_EMULATED`, `BOOST_COMP_MWERKS_AVAILABLE`, `BOOST_COMP_MWERKS_NAME`. Display-name macros are `BOOST_COMP_MWERKS_NAME` "Metrowerks CodeWarrior". Predef test registrations are `BOOST_COMP_MWERKS,BOOST_COMP_MWERKS_NAME`, `BOOST_COMP_MWERKS_EMULATED,BOOST_COMP_MWERKS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__MWERKS__`, `__CWCC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/metrowerks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/microtec.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/microtec.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/microtec.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_MRI`, `BOOST_COMP_MRI_DETECTION`, `BOOST_COMP_MRI_EMULATED`. Other relevant macros in this header include `BOOST_COMP_MRI`, `BOOST_COMP_MRI_DETECTION`, `BOOST_COMP_MRI_EMULATED`, `BOOST_COMP_MRI_AVAILABLE`, `BOOST_COMP_MRI_NAME`. Display-name macros are `BOOST_COMP_MRI_NAME` "Microtec C/C++". Predef test registrations are `BOOST_COMP_MRI,BOOST_COMP_MRI_NAME`, `BOOST_COMP_MRI_EMULATED,BOOST_COMP_MRI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_MRI`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/microtec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/mpw.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/mpw.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/mpw.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_MPW`, `BOOST_COMP_MPW_DETECTION`, `BOOST_COMP_MPW_EMULATED`. Other relevant macros in this header include `BOOST_COMP_MPW`, `BOOST_COMP_MPW_DETECTION`, `BOOST_COMP_MPW_EMULATED`, `BOOST_COMP_MPW_AVAILABLE`, `BOOST_COMP_MPW_NAME`. Display-name macros are `BOOST_COMP_MPW_NAME` "MPW C++". Predef test registrations are `BOOST_COMP_MPW,BOOST_COMP_MPW_NAME`, `BOOST_COMP_MPW_EMULATED,BOOST_COMP_MPW_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__MRC__`, `MPW_C`, `MPW_CPLUS`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/mpw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/nvcc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/nvcc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/nvcc.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_NVCC`, `BOOST_COMP_NVCC_DETECTION`. Other relevant macros in this header include `BOOST_COMP_NVCC`, `BOOST_COMP_NVCC_DETECTION`, `BOOST_COMP_NVCC_AVAILABLE`, `BOOST_COMP_NVCC_NAME`. Display-name macros are `BOOST_COMP_NVCC_NAME` "NVCC". Predef test registrations are `BOOST_COMP_NVCC,BOOST_COMP_NVCC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__NVCC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/nvcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/palm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/palm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/palm.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_PALM`, `BOOST_COMP_PALM_DETECTION`, `BOOST_COMP_PALM_EMULATED`. Other relevant macros in this header include `BOOST_COMP_PALM`, `BOOST_COMP_PALM_DETECTION`, `BOOST_COMP_PALM_EMULATED`, `BOOST_COMP_PALM_AVAILABLE`, `BOOST_COMP_PALM_NAME`. Display-name macros are `BOOST_COMP_PALM_NAME` "Palm C/C++". Predef test registrations are `BOOST_COMP_PALM,BOOST_COMP_PALM_NAME`, `BOOST_COMP_PALM_EMULATED,BOOST_COMP_PALM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_PACC_VER`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/palm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/pgi.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/pgi.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/pgi.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_PGI`, `BOOST_COMP_PGI_DETECTION`, `BOOST_COMP_PGI_EMULATED`. Other relevant macros in this header include `BOOST_COMP_PGI`, `BOOST_COMP_PGI_DETECTION`, `BOOST_COMP_PGI_EMULATED`, `BOOST_COMP_PGI_AVAILABLE`, `BOOST_COMP_PGI_NAME`. Display-name macros are `BOOST_COMP_PGI_NAME` "Portland Group C/C++". Predef test registrations are `BOOST_COMP_PGI,BOOST_COMP_PGI_NAME`, `BOOST_COMP_PGI_EMULATED,BOOST_COMP_PGI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__PGI`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/pgi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sgi_mipspro.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sgi_mipspro.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sgi_mipspro.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_SGI`, `BOOST_COMP_SGI_DETECTION`, `BOOST_COMP_SGI_EMULATED`. Other relevant macros in this header include `BOOST_COMP_SGI`, `BOOST_COMP_SGI_DETECTION`, `BOOST_COMP_SGI_EMULATED`, `BOOST_COMP_SGI_AVAILABLE`, `BOOST_COMP_SGI_NAME`. Display-name macros are `BOOST_COMP_SGI_NAME` "SGI MIPSpro". Predef test registrations are `BOOST_COMP_SGI,BOOST_COMP_SGI_NAME`, `BOOST_COMP_SGI_EMULATED,BOOST_COMP_SGI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__sgi`, `sgi`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sgi_mipspro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sunpro.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sunpro.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sunpro.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_SUNPRO`, `BOOST_COMP_SUNPRO_DETECTION`, `BOOST_COMP_SUNPRO_EMULATED`. Other relevant macros in this header include `BOOST_COMP_SUNPRO`, `BOOST_COMP_SUNPRO_DETECTION`, `BOOST_COMP_SUNPRO_EMULATED`, `BOOST_COMP_SUNPRO_AVAILABLE`, `BOOST_COMP_SUNPRO_NAME`. Display-name macros are `BOOST_COMP_SUNPRO_NAME` "Oracle Solaris Studio". Predef test registrations are `BOOST_COMP_SUNPRO,BOOST_COMP_SUNPRO_NAME`, `BOOST_COMP_SUNPRO_EMULATED,BOOST_COMP_SUNPRO_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__SUNPRO_CC`, `__SUNPRO_C`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/sunpro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/tendra.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/tendra.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/tendra.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_TENDRA`, `BOOST_COMP_TENDRA_DETECTION`, `BOOST_COMP_TENDRA_EMULATED`. Other relevant macros in this header include `BOOST_COMP_TENDRA`, `BOOST_COMP_TENDRA_DETECTION`, `BOOST_COMP_TENDRA_EMULATED`, `BOOST_COMP_TENDRA_AVAILABLE`, `BOOST_COMP_TENDRA_NAME`. Display-name macros are `BOOST_COMP_TENDRA_NAME` "TenDRA C/C++". Predef test registrations are `BOOST_COMP_TENDRA,BOOST_COMP_TENDRA_NAME`, `BOOST_COMP_TENDRA_EMULATED,BOOST_COMP_TENDRA_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__TenDRA__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/tendra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/visualc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/visualc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/visualc.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_MSVC`, `BOOST_COMP_MSVC_BUILD`, `BOOST_COMP_MSVC_DETECTION`, `BOOST_COMP_MSVC_EMULATED`. Other relevant macros in this header include `BOOST_COMP_MSVC`, `BOOST_COMP_MSVC_BUILD`, `BOOST_COMP_MSVC_DETECTION`, `BOOST_COMP_MSVC_EMULATED`, `BOOST_COMP_MSVC_AVAILABLE`, `BOOST_COMP_MSVC_NAME`. Display-name macros are `BOOST_COMP_MSVC_NAME` "Microsoft Visual C/C++". Predef test registrations are `BOOST_COMP_MSVC,BOOST_COMP_MSVC_NAME`, `BOOST_COMP_MSVC_EMULATED,BOOST_COMP_MSVC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_MSC_VER`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/compiler/clang.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/visualc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/watcom.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/watcom.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/watcom.h` is a Boost.Predef compiler detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_COMP_WATCOM`, `BOOST_COMP_WATCOM_DETECTION`, `BOOST_COMP_WATCOM_EMULATED`. Other relevant macros in this header include `BOOST_COMP_WATCOM`, `BOOST_COMP_WATCOM_DETECTION`, `BOOST_COMP_WATCOM_EMULATED`, `BOOST_COMP_WATCOM_AVAILABLE`, `BOOST_COMP_WATCOM_NAME`. Display-name macros are `BOOST_COMP_WATCOM_NAME` "Watcom C++". Predef test registrations are `BOOST_COMP_WATCOM,BOOST_COMP_WATCOM_NAME`, `BOOST_COMP_WATCOM_EMULATED,BOOST_COMP_WATCOM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__WATCOMC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. Compiler detectors also respect `BOOST_PREDEF_DETAIL_COMP_DETECTED`, marking later matches as `*_EMULATED` when another compiler header already claimed the primary compiler.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/comp_detected.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/compiler/watcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h` is a Boost.Predef detail header for assert configuration shim. It conditionally includes `<assert.h>` only when predef tests are enabled and `NDEBUG` is not set.

## Important APIs, Types, and Functions

The exposed preprocessor surface is none. Direct includes are `cassert`, `assert.h`. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_exception.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_exception.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_exception.h` is a Boost.Predef detail header for exception configuration shim. It conditionally includes `<exception>` for standard-library detection probes when exceptions support is visible.

## Important APIs, Types, and Functions

The exposed preprocessor surface is none. Direct includes are `exception`. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/comp_detected.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/comp_detected.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/comp_detected.h` is a Boost.Predef detail header for compiler-detected sentinel. It defines `BOOST_PREDEF_DETAIL_COMP_DETECTED` so later compiler headers can mark themselves as emulated instead of primary.

## Important APIs, Types, and Functions

The exposed preprocessor surface is `BOOST_PREDEF_DETAIL_COMP_DETECTED`. Direct includes are none. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/comp_detected.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/os_detected.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/os_detected.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/os_detected.h` is a Boost.Predef detail header for OS-detected sentinel. It defines `BOOST_PREDEF_DETAIL_OS_DETECTED` so mutually exclusive OS detectors do not all claim primary detection.

## Important APIs, Types, and Functions

The exposed preprocessor surface is `BOOST_PREDEF_DETAIL_OS_DETECTED`. Direct includes are none. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/os_detected.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/platform_detected.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/platform_detected.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/platform_detected.h` is a Boost.Predef detail header for platform-detected sentinel. It defines `BOOST_PREDEF_DETAIL_PLAT_DETECTED` for platform detector ordering.

## Important APIs, Types, and Functions

The exposed preprocessor surface is `BOOST_PREDEF_DETAIL_PLAT_DETECTED`. Direct includes are none. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/platform_detected.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/test.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/test.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/test.h` is a Boost.Predef detail header for predef self-test registration shim. It declares `BOOST_PREDEF_DECLARE_TEST` and `BOOST_PREDEF_DECLARE_TEST_WITH_NAME`; in this vendored non-test build both macros expand away.

## Important APIs, Types, and Functions

The exposed preprocessor surface is `BOOST_PREDEF_DECLARE_TEST`. Direct includes are none. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware.h` is a umbrella hardware include that currently gathers SIMD hardware capability predefs. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/hardware/simd.h`. Consumers normally include this file when they want the whole `hardware.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/hardware.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h` is the aggregate SIMD hardware detector. It includes the x86, x86 AMD extension, ARM, and PPC SIMD detectors and exposes one overall `BOOST_HW_SIMD` value when exactly one architecture family is active.

## Important APIs, Types, and Functions

The main macros are `BOOST_HW_SIMD`, `BOOST_HW_SIMD_AVAILABLE`, and `BOOST_HW_SIMD_NAME`. Direct includes are `boost/predef/hardware/simd/x86.h`, `boost/predef/hardware/simd/x86_amd.h`, `boost/predef/hardware/simd/arm.h`, `boost/predef/hardware/simd/ppc.h`, `boost/predef/version_number.h`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/detail/test.h`.

## Control Flow

After including architecture-specific SIMD headers, the file errors if incompatible SIMD architecture families are simultaneously detected. If both `BOOST_HW_SIMD_X86` and `BOOST_HW_SIMD_X86_AMD` are available, it chooses the larger version. Otherwise it copies the single active architecture value or falls back to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`.

## State and Persistence Behavior

The file has no runtime state. Its result is a translation-unit-local preprocessor macro derived from the target flags and architecture macros visible during compilation.

## Dependencies and Integration Points

It is included by `boost/predef/hardware.h` and ultimately by `boost/predef.h`. Code that only needs to know whether any SIMD extension is enabled can include this aggregate instead of checking each architecture-specific header.

## Risks and Edge Cases

The mutual-exclusion check assumes a single target architecture. Unusual compiler environments that expose multiple architecture feature sets can trigger the explicit error. The x86/x86_amd merge needs numeric version ordering to remain consistent with the version tables.

## Test Signals

Build small probes with no SIMD flags, with x86 SSE/AVX flags, with ARM NEON target flags, and with PPC VMX/VSX flags. Confirm `BOOST_HW_SIMD_AVAILABLE` and the selected numeric value match the strongest enabled extension.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h` detects SIMD hardware support for its architecture family and reports the highest enabled extension as a Boost.Predef version macro. SIMD detection is driven by compiler target flags and predefined feature macros.

## Important APIs, Types, and Functions

Primary reported macros are `BOOST_HW_SIMD_ARM`. Related macros include `BOOST_HW_SIMD_ARM`, `BOOST_HW_SIMD_ARM_AVAILABLE`, `BOOST_HW_SIMD_ARM_NAME`. Display-name macros are `BOOST_HW_SIMD_ARM_NAME` "ARM SIMD". Direct includes are `boost/predef/version_number.h`, `boost/predef/hardware/simd/arm/versions.h`, `boost/predef/detail/test.h`.

## Control Flow

The detector starts with its `BOOST_HW_SIMD_*` macro set to not available, then checks architecture/compiler feature symbols such as `__ARM_NEON__`, `__aarch64__`, `_M_ARM`, `_M_ARM64`. Matching branches assign the newest supported version constant from the sibling `versions.h` table, define `*_AVAILABLE`, and register a predef test.

## State and Persistence Behavior

There is no runtime state. Detection results are macros that persist only for the current translation unit and depend on compiler options such as x86 `-mavx`, ARM NEON flags, or PPC VMX/VSX flags.

## Dependencies and Integration Points

This file feeds `boost/predef/hardware/simd.h`, which chooses the overall `BOOST_HW_SIMD` value and guards against incompatible multi-architecture SIMD detections. Mergerfs can use it through vendored Boost for conditional compilation of target-specific code.

## Risks and Edge Cases

SIMD macros are inclusive and compiler-option dependent, so a host CPU may support an instruction set that is not reported unless the compiler target enables it. Cross-compilation can expose target macros unrelated to the build host. Visual C++ and GCC/Clang expose different granularity.

## Test Signals

Compile preprocessor probes with representative target flags and assert the selected `BOOST_HW_SIMD_*` value. Include negative builds with no SIMD flags and cross-target builds to ensure only the intended architecture-specific availability macro is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm/versions.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm/versions.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm/versions.h` defines symbolic Boost.Predef version constants for ARM SIMD instruction-set levels. The constants let callers compare `BOOST_HW_SIMD_*` detector values without hard-coding `BOOST_VERSION_NUMBER` tuples.

## Important APIs, Types, and Functions

Version macros in this file include `BOOST_HW_SIMD_ARM_NEON_VERSION`. Direct includes are `boost/predef/version_number.h`.

## Control Flow

There is no conditional detection. The header is a constant table guarded by an include guard; detector headers include it and then choose the highest enabled version based on compiler predefined feature macros.

## State and Persistence Behavior

The file is preprocessor-only and stateless. The constants persist as macros in the current translation unit.

## Dependencies and Integration Points

It integrates with the sibling SIMD detector for the same architecture and with `boost/predef/hardware/simd.h`, which selects an overall `BOOST_HW_SIMD` value from architecture-specific detections.

## Risks and Edge Cases

Incorrect ordering or numeric values would break range comparisons such as `>= SSE2_VERSION`. New instruction-set levels require updates here and in the detector header that maps compiler macros to these constants.

## Test Signals

Preprocessor tests should assert monotonic ordering of the version constants and compile detector checks under compiler flags that enable representative SIMD levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm/versions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc.h` detects SIMD hardware support for its architecture family and reports the highest enabled extension as a Boost.Predef version macro. SIMD detection is driven by compiler target flags and predefined feature macros.

## Important APIs, Types, and Functions

Primary reported macros are `BOOST_HW_SIMD_PPC`. Related macros include `BOOST_HW_SIMD_PPC`, `BOOST_HW_SIMD_PPC_AVAILABLE`, `BOOST_HW_SIMD_PPC_NAME`. Display-name macros are `BOOST_HW_SIMD_PPC_NAME` "PPC SIMD". Direct includes are `boost/predef/version_number.h`, `boost/predef/hardware/simd/ppc/versions.h`, `boost/predef/detail/test.h`.

## Control Flow

The detector starts with its `BOOST_HW_SIMD_*` macro set to not available, then checks architecture/compiler feature symbols such as `__VECTOR4DOUBLE__`, `__VSX__`, `__ALTIVEC__`, `__VEC__`. Matching branches assign the newest supported version constant from the sibling `versions.h` table, define `*_AVAILABLE`, and register a predef test.

## State and Persistence Behavior

There is no runtime state. Detection results are macros that persist only for the current translation unit and depend on compiler options such as x86 `-mavx`, ARM NEON flags, or PPC VMX/VSX flags.

## Dependencies and Integration Points

This file feeds `boost/predef/hardware/simd.h`, which chooses the overall `BOOST_HW_SIMD` value and guards against incompatible multi-architecture SIMD detections. Mergerfs can use it through vendored Boost for conditional compilation of target-specific code.

## Risks and Edge Cases

SIMD macros are inclusive and compiler-option dependent, so a host CPU may support an instruction set that is not reported unless the compiler target enables it. Cross-compilation can expose target macros unrelated to the build host. Visual C++ and GCC/Clang expose different granularity.

## Test Signals

Compile preprocessor probes with representative target flags and assert the selected `BOOST_HW_SIMD_*` value. Include negative builds with no SIMD flags and cross-target builds to ensure only the intended architecture-specific availability macro is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc/versions.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc/versions.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc/versions.h` defines symbolic Boost.Predef version constants for PPC SIMD instruction-set levels. The constants let callers compare `BOOST_HW_SIMD_*` detector values without hard-coding `BOOST_VERSION_NUMBER` tuples.

## Important APIs, Types, and Functions

Version macros in this file include `BOOST_HW_SIMD_PPC_VMX_VERSION`, `BOOST_HW_SIMD_PPC_VSX_VERSION`, `BOOST_HW_SIMD_PPC_QPX_VERSION`. Direct includes are `boost/predef/version_number.h`.

## Control Flow

There is no conditional detection. The header is a constant table guarded by an include guard; detector headers include it and then choose the highest enabled version based on compiler predefined feature macros.

## State and Persistence Behavior

The file is preprocessor-only and stateless. The constants persist as macros in the current translation unit.

## Dependencies and Integration Points

It integrates with the sibling SIMD detector for the same architecture and with `boost/predef/hardware/simd.h`, which selects an overall `BOOST_HW_SIMD` value from architecture-specific detections.

## Risks and Edge Cases

Incorrect ordering or numeric values would break range comparisons such as `>= SSE2_VERSION`. New instruction-set levels require updates here and in the detector header that maps compiler macros to these constants.

## Test Signals

Preprocessor tests should assert monotonic ordering of the version constants and compile detector checks under compiler flags that enable representative SIMD levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/ppc/versions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86.h` detects SIMD hardware support for its architecture family and reports the highest enabled extension as a Boost.Predef version macro. SIMD detection is driven by compiler target flags and predefined feature macros.

## Important APIs, Types, and Functions

Primary reported macros are `BOOST_HW_SIMD_X86`. Related macros include `BOOST_HW_SIMD_X86`, `BOOST_HW_SIMD_X86_AVAILABLE`, `BOOST_HW_SIMD_X86_NAME`. Display-name macros are `BOOST_HW_SIMD_X86_NAME` "x86 SIMD". Direct includes are `boost/predef/version_number.h`, `boost/predef/hardware/simd/x86/versions.h`, `boost/predef/detail/test.h`.

## Control Flow

The detector starts with its `BOOST_HW_SIMD_*` macro set to not available, then checks architecture/compiler feature symbols such as `__MIC__`, `__AVX2__`, `__AVX__`, `__FMA__`, `__SSE4_2__`, `__SSE4_1__`, `__SSSE3__`, `__SSE3__`, `__SSE2__`, `_M_X64`, `_M_IX86_FP`, `__SSE__`. Matching branches assign the newest supported version constant from the sibling `versions.h` table, define `*_AVAILABLE`, and register a predef test.

## State and Persistence Behavior

There is no runtime state. Detection results are macros that persist only for the current translation unit and depend on compiler options such as x86 `-mavx`, ARM NEON flags, or PPC VMX/VSX flags.

## Dependencies and Integration Points

This file feeds `boost/predef/hardware/simd.h`, which chooses the overall `BOOST_HW_SIMD` value and guards against incompatible multi-architecture SIMD detections. Mergerfs can use it through vendored Boost for conditional compilation of target-specific code.

## Risks and Edge Cases

SIMD macros are inclusive and compiler-option dependent, so a host CPU may support an instruction set that is not reported unless the compiler target enables it. Cross-compilation can expose target macros unrelated to the build host. Visual C++ and GCC/Clang expose different granularity.

## Test Signals

Compile preprocessor probes with representative target flags and assert the selected `BOOST_HW_SIMD_*` value. Include negative builds with no SIMD flags and cross-target builds to ensure only the intended architecture-specific availability macro is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h` defines symbolic Boost.Predef version constants for X86 SIMD instruction-set levels. The constants let callers compare `BOOST_HW_SIMD_*` detector values without hard-coding `BOOST_VERSION_NUMBER` tuples.

## Important APIs, Types, and Functions

Version macros in this file include `BOOST_HW_SIMD_X86_MMX_VERSION`, `BOOST_HW_SIMD_X86_SSE_VERSION`, `BOOST_HW_SIMD_X86_SSE2_VERSION`, `BOOST_HW_SIMD_X86_SSE3_VERSION`, `BOOST_HW_SIMD_X86_SSSE3_VERSION`, `BOOST_HW_SIMD_X86_SSE4_1_VERSION`, `BOOST_HW_SIMD_X86_SSE4_2_VERSION`, `BOOST_HW_SIMD_X86_AVX_VERSION`, `BOOST_HW_SIMD_X86_FMA3_VERSION`, `BOOST_HW_SIMD_X86_AVX2_VERSION`, `BOOST_HW_SIMD_X86_MIC_VERSION`. Direct includes are `boost/predef/version_number.h`.

## Control Flow

There is no conditional detection. The header is a constant table guarded by an include guard; detector headers include it and then choose the highest enabled version based on compiler predefined feature macros.

## State and Persistence Behavior

The file is preprocessor-only and stateless. The constants persist as macros in the current translation unit.

## Dependencies and Integration Points

It integrates with the sibling SIMD detector for the same architecture and with `boost/predef/hardware/simd.h`, which selects an overall `BOOST_HW_SIMD` value from architecture-specific detections.

## Risks and Edge Cases

Incorrect ordering or numeric values would break range comparisons such as `>= SSE2_VERSION`. New instruction-set levels require updates here and in the detector header that maps compiler macros to these constants.

## Test Signals

Preprocessor tests should assert monotonic ordering of the version constants and compile detector checks under compiler flags that enable representative SIMD levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd.h` detects SIMD hardware support for its architecture family and reports the highest enabled extension as a Boost.Predef version macro. SIMD detection is driven by compiler target flags and predefined feature macros.

## Important APIs, Types, and Functions

Primary reported macros are `BOOST_HW_SIMD_X86_AMD`. Related macros include `BOOST_HW_SIMD_X86_AMD`, `BOOST_HW_SIMD_X86_AMD_AVAILABLE`, `BOOST_HW_SIMD_X86_AMD_NAME`. Display-name macros are `BOOST_HW_SIMD_X86_AMD_NAME` "x86 (AMD) SIMD". Direct includes are `boost/predef/version_number.h`, `boost/predef/hardware/simd/x86_amd/versions.h`, `boost/predef/hardware/simd/x86.h`, `boost/predef/detail/test.h`.

## Control Flow

The detector starts with its `BOOST_HW_SIMD_*` macro set to not available, then checks architecture/compiler feature symbols such as `__XOP__`, `__FMA4__`, `__SSE4A__`. Matching branches assign the newest supported version constant from the sibling `versions.h` table, define `*_AVAILABLE`, and register a predef test.

## State and Persistence Behavior

There is no runtime state. Detection results are macros that persist only for the current translation unit and depend on compiler options such as x86 `-mavx`, ARM NEON flags, or PPC VMX/VSX flags.

## Dependencies and Integration Points

This file feeds `boost/predef/hardware/simd.h`, which chooses the overall `BOOST_HW_SIMD` value and guards against incompatible multi-architecture SIMD detections. Mergerfs can use it through vendored Boost for conditional compilation of target-specific code.

## Risks and Edge Cases

SIMD macros are inclusive and compiler-option dependent, so a host CPU may support an instruction set that is not reported unless the compiler target enables it. Cross-compilation can expose target macros unrelated to the build host. Visual C++ and GCC/Clang expose different granularity.

## Test Signals

Compile preprocessor probes with representative target flags and assert the selected `BOOST_HW_SIMD_*` value. Include negative builds with no SIMD flags and cross-target builds to ensure only the intended architecture-specific availability macro is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd/versions.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd/versions.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd/versions.h` defines symbolic Boost.Predef version constants for X86 AMD SIMD instruction-set levels. The constants let callers compare `BOOST_HW_SIMD_*` detector values without hard-coding `BOOST_VERSION_NUMBER` tuples.

## Important APIs, Types, and Functions

Version macros in this file include `BOOST_HW_SIMD_X86_AMD_SSE4A_VERSION`, `BOOST_HW_SIMD_X86_AMD_FMA4_VERSION`, `BOOST_HW_SIMD_X86_AMD_XOP_VERSION`. Direct includes are `boost/predef/version_number.h`.

## Control Flow

There is no conditional detection. The header is a constant table guarded by an include guard; detector headers include it and then choose the highest enabled version based on compiler predefined feature macros.

## State and Persistence Behavior

The file is preprocessor-only and stateless. The constants persist as macros in the current translation unit.

## Dependencies and Integration Points

It integrates with the sibling SIMD detector for the same architecture and with `boost/predef/hardware/simd.h`, which selects an overall `BOOST_HW_SIMD` value from architecture-specific detections.

## Risks and Edge Cases

Incorrect ordering or numeric values would break range comparisons such as `>= SSE2_VERSION`. New instruction-set levels require updates here and in the detector header that maps compiler macros to these constants.

## Test Signals

Preprocessor tests should assert monotonic ordering of the version constants and compile detector checks under compiler flags that enable representative SIMD levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86_amd/versions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language.h` is a umbrella language include for CUDA, Objective-C, C, and C++ language-standard detection headers. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/language/stdc.h`, `boost/predef/language/stdcpp.h`, `boost/predef/language/objc.h`, `boost/predef/language/cuda.h`. Consumers normally include this file when they want the whole `language.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/language.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/cuda.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language/cuda.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language/cuda.h` detects language-standard availability for a Boost.Predef language family.

## Important APIs, Types, and Functions

Primary macros are `BOOST_LANG_CUDA`. Related macros include `BOOST_LANG_CUDA`, `BOOST_LANG_CUDA_AVAILABLE`, `BOOST_LANG_CUDA_NAME`. Display-name macros are `BOOST_LANG_CUDA_NAME` "CUDA C/C++". Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `cuda.h`, `boost/predef/detail/test.h`.

## Control Flow

The file initializes each language macro to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, then checks language predefined symbols such as `__CUDACC__`, `__CUDA__`. When a symbol is present it normalizes the value with `BOOST_PREDEF_MAKE_*` helpers or assigns `BOOST_VERSION_NUMBER_AVAILABLE`, defines `*_AVAILABLE`, and registers a Predef test.

## State and Persistence Behavior

No runtime state or persistence is involved. The macros reflect the language mode selected for the current translation unit, such as C++ standard level, CUDA compilation, or Objective-C enablement.

## Dependencies and Integration Points

Language detectors are included by `boost/predef/language.h` and the umbrella `boost/predef.h`. Vendored Boost users can use them to select code paths that require specific language front-end support.

## Risks and Edge Cases

Compiler-reported language macros can lag the actual supported features or use draft standard dates. CUDA and Objective-C modes may be enabled only for specific compiler phases. Code should compare against documented Predef versions rather than raw vendor values.

## Test Signals

Compile preprocessor probes under multiple language standards and front-end modes, then assert the expected `BOOST_LANG_*` value and `*_AVAILABLE` marker. Negative tests should compile in modes where the language extension is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/cuda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h` detects language-standard availability for a Boost.Predef language family.

## Important APIs, Types, and Functions

Primary macros are `BOOST_LANG_OBJC`. Related macros include `BOOST_LANG_OBJC`, `BOOST_LANG_OBJC_AVAILABLE`, `BOOST_LANG_OBJC_NAME`. Display-name macros are `BOOST_LANG_OBJC_NAME` "Objective-C". Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`.

## Control Flow

The file initializes each language macro to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, then checks language predefined symbols such as `__OBJC__`. When a symbol is present it normalizes the value with `BOOST_PREDEF_MAKE_*` helpers or assigns `BOOST_VERSION_NUMBER_AVAILABLE`, defines `*_AVAILABLE`, and registers a Predef test.

## State and Persistence Behavior

No runtime state or persistence is involved. The macros reflect the language mode selected for the current translation unit, such as C++ standard level, CUDA compilation, or Objective-C enablement.

## Dependencies and Integration Points

Language detectors are included by `boost/predef/language.h` and the umbrella `boost/predef.h`. Vendored Boost users can use them to select code paths that require specific language front-end support.

## Risks and Edge Cases

Compiler-reported language macros can lag the actual supported features or use draft standard dates. CUDA and Objective-C modes may be enabled only for specific compiler phases. Code should compare against documented Predef versions rather than raw vendor values.

## Test Signals

Compile preprocessor probes under multiple language standards and front-end modes, then assert the expected `BOOST_LANG_*` value and `*_AVAILABLE` marker. Negative tests should compile in modes where the language extension is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdc.h` detects language-standard availability for a Boost.Predef language family. This file covers Standard C language and related hosted/IEC feature-level macros.

## Important APIs, Types, and Functions

Primary macros are `BOOST_LANG_STDC`. Related macros include `BOOST_LANG_STDC`, `BOOST_LANG_STDC_AVAILABLE`, `BOOST_LANG_STDC_NAME`. Display-name macros are `BOOST_LANG_STDC_NAME` "Standard C". Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`.

## Control Flow

The file initializes each language macro to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, then checks language predefined symbols such as `__STDC__`. When a symbol is present it normalizes the value with `BOOST_PREDEF_MAKE_*` helpers or assigns `BOOST_VERSION_NUMBER_AVAILABLE`, defines `*_AVAILABLE`, and registers a Predef test.

## State and Persistence Behavior

No runtime state or persistence is involved. The macros reflect the language mode selected for the current translation unit, such as C++ standard level, CUDA compilation, or Objective-C enablement.

## Dependencies and Integration Points

Language detectors are included by `boost/predef/language.h` and the umbrella `boost/predef.h`. Vendored Boost users can use them to select code paths that require specific language front-end support.

## Risks and Edge Cases

Compiler-reported language macros can lag the actual supported features or use draft standard dates. CUDA and Objective-C modes may be enabled only for specific compiler phases. Code should compare against documented Predef versions rather than raw vendor values.

## Test Signals

Compile preprocessor probes under multiple language standards and front-end modes, then assert the expected `BOOST_LANG_*` value and `*_AVAILABLE` marker. Negative tests should compile in modes where the language extension is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdcpp.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdcpp.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdcpp.h` detects language-standard availability for a Boost.Predef language family. This file contains three detectors: Standard C++, C++/CLI, and Embedded C++.

## Important APIs, Types, and Functions

Primary macros are `BOOST_LANG_STDCPP`, `BOOST_LANG_STDCPPCLI`, `BOOST_LANG_STDECPP`. Related macros include `BOOST_LANG_STDCPP`, `BOOST_LANG_STDCPP_AVAILABLE`, `BOOST_LANG_STDCPP_NAME`, `BOOST_LANG_STDCPPCLI`, `BOOST_LANG_STDCPPCLI_AVAILABLE`, `BOOST_LANG_STDCPPCLI_NAME`, `BOOST_LANG_STDECPP`, `BOOST_LANG_STDECPP_AVAILABLE`, `BOOST_LANG_STDECPP_NAME`. Display-name macros are `BOOST_LANG_STDCPP_NAME` "Standard C++", `BOOST_LANG_STDCPPCLI_NAME` "Standard C++/CLI", `BOOST_LANG_STDECPP_NAME` "Standard Embedded C++". Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`, `boost/predef/detail/test.h`.

## Control Flow

The file initializes each language macro to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, then checks language predefined symbols such as `__cplusplus`, `__cplusplus_cli`, `__embedded_cplusplus`. When a symbol is present it normalizes the value with `BOOST_PREDEF_MAKE_*` helpers or assigns `BOOST_VERSION_NUMBER_AVAILABLE`, defines `*_AVAILABLE`, and registers a Predef test.

## State and Persistence Behavior

No runtime state or persistence is involved. The macros reflect the language mode selected for the current translation unit, such as C++ standard level, CUDA compilation, or Objective-C enablement.

## Dependencies and Integration Points

Language detectors are included by `boost/predef/language.h` and the umbrella `boost/predef.h`. Vendored Boost users can use them to select code paths that require specific language front-end support.

## Risks and Edge Cases

Compiler-reported language macros can lag the actual supported features or use draft standard dates. CUDA and Objective-C modes may be enabled only for specific compiler phases. Code should compare against documented Predef versions rather than raw vendor values.

## Test Signals

Compile preprocessor probes under multiple language standards and front-end modes, then assert the expected `BOOST_LANG_*` value and `*_AVAILABLE` marker. Negative tests should compile in modes where the language extension is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/stdcpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library.h` is a umbrella library include for C and C++ standard-library implementation detection. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/library/c.h`, `boost/predef/library/std.h`. Consumers normally include this file when they want the whole `library.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/library.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c.h` is a umbrella C library include that includes the C runtime prefix and known C library detectors. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/library/c/_prefix.h`, `boost/predef/library/c/cloudabi.h`, `boost/predef/library/c/gnu.h`, `boost/predef/library/c/uc.h`, `boost/predef/library/c/vms.h`, `boost/predef/library/c/zos.h`. Consumers normally include this file when they want the whole `library/c.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/library/c.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/_prefix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/_prefix.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/_prefix.h` is the shared prefix header for Boost.Predef C runtime library detectors. It performs conservative setup before individual library implementation probes run.

## Important APIs, Types, and Functions

Direct includes are `boost/predef/detail/_cassert.h`. The file intentionally exposes little or no public macro surface; child detectors define the user-facing `BOOST_LIB_*` macros.

## Control Flow

The include guard prevents duplicate setup. Any conditional include in the prefix runs before implementation-specific headers test vendor library macros, ensuring required standard declarations or feature macros are visible when available.

## State and Persistence Behavior

The header creates no runtime state. Its only persistence is preprocessor include state and any macros made visible by the setup includes.

## Dependencies and Integration Points

It is included by sibling `cloudabi`, `gnu`, `dinkumware`, `libc++`, and similar library detector headers. The prefix keeps common probing assumptions in one place.

## Risks and Edge Cases

Library detection is sensitive to include order and to whether standard headers have already been included. The prefix must stay lightweight so freestanding or partial standard-library environments can still include Boost.Predef.

## Test Signals

Compile the parent library aggregation headers across libstdc++, libc++, MSVC STL, and C runtime variants. Confirm the prefix does not force unavailable standard headers in constrained builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/_prefix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/cloudabi.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/cloudabi.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/cloudabi.h` is a Boost.Predef C library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_C_CLOUDABI`. Other relevant macros in this header include `BOOST_LIB_C_CLOUDABI`, `BOOST_LIB_C_CLOUDABI_AVAILABLE`, `BOOST_LIB_C_CLOUDABI_NAME`. Display-name macros are `BOOST_LIB_C_CLOUDABI_NAME` "cloudlibc". Predef test registrations are `BOOST_LIB_C_CLOUDABI,BOOST_LIB_C_CLOUDABI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__CloudABI__`, `__cloudlibc__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/library/c/_prefix.h`, `stddef.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/cloudabi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/gnu.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/gnu.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/gnu.h` is a Boost.Predef C library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_C_GNU`. Other relevant macros in this header include `BOOST_LIB_C_GNU`, `BOOST_LIB_C_GNU_AVAILABLE`, `BOOST_LIB_C_GNU_NAME`. Display-name macros are `BOOST_LIB_C_GNU_NAME` "GNU". Predef test registrations are `BOOST_LIB_C_GNU,BOOST_LIB_C_GNU_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__STDC__`, `__cplusplus`, `__GLIBC__`, `__GNU_LIBRARY__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/library/c/_prefix.h`, `stddef.h`, `cstddef`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/gnu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/uc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/uc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/uc.h` is a Boost.Predef C library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_C_UC`. Other relevant macros in this header include `BOOST_LIB_C_UC`, `BOOST_LIB_C_UC_AVAILABLE`, `BOOST_LIB_C_UC_NAME`. Display-name macros are `BOOST_LIB_C_UC_NAME` "uClibc". Predef test registrations are `BOOST_LIB_C_UC,BOOST_LIB_C_UC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__UCLIBC__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/c/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/uc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/vms.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/vms.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/vms.h` is a Boost.Predef C library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_C_VMS`. Other relevant macros in this header include `BOOST_LIB_C_VMS`, `BOOST_LIB_C_VMS_AVAILABLE`, `BOOST_LIB_C_VMS_NAME`. Display-name macros are `BOOST_LIB_C_VMS_NAME` "VMS". Predef test registrations are `BOOST_LIB_C_VMS,BOOST_LIB_C_VMS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__CRTL_VER`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/c/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/vms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/zos.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/zos.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/zos.h` is a Boost.Predef C library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_C_ZOS`. Other relevant macros in this header include `BOOST_LIB_C_ZOS`, `BOOST_LIB_C_ZOS_AVAILABLE`, `BOOST_LIB_C_ZOS_NAME`. Display-name macros are `BOOST_LIB_C_ZOS_NAME` "z/OS". Predef test registrations are `BOOST_LIB_C_ZOS,BOOST_LIB_C_ZOS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__LIBREL__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/c/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/c/zos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h` is a umbrella C++ standard-library include that includes the stdlib prefix and known implementation detectors. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/library/std/cxx.h`, `boost/predef/library/std/dinkumware.h`, `boost/predef/library/std/libcomo.h`, `boost/predef/library/std/modena.h`, `boost/predef/library/std/msl.h`, `boost/predef/library/std/msvc.h`, `boost/predef/library/std/roguewave.h`, `boost/predef/library/std/sgi.h`, `boost/predef/library/std/stdcpp3.h`, `boost/predef/library/std/stlport.h`, `boost/predef/library/std/vacpp.h`. Consumers normally include this file when they want the whole `library/std.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h` is the shared prefix header for Boost.Predef C++ standard library detectors. It performs conservative setup before individual library implementation probes run.

## Important APIs, Types, and Functions

Direct includes are `boost/predef/detail/_exception.h`. The file intentionally exposes little or no public macro surface; child detectors define the user-facing `BOOST_LIB_*` macros.

## Control Flow

The include guard prevents duplicate setup. Any conditional include in the prefix runs before implementation-specific headers test vendor library macros, ensuring required standard declarations or feature macros are visible when available.

## State and Persistence Behavior

The header creates no runtime state. Its only persistence is preprocessor include state and any macros made visible by the setup includes.

## Dependencies and Integration Points

It is included by sibling `cloudabi`, `gnu`, `dinkumware`, `libc++`, and similar library detector headers. The prefix keeps common probing assumptions in one place.

## Risks and Edge Cases

Library detection is sensitive to include order and to whether standard headers have already been included. The prefix must stay lightweight so freestanding or partial standard-library environments can still include Boost.Predef.

## Test Signals

Compile the parent library aggregation headers across libstdc++, libc++, MSVC STL, and C runtime variants. Confirm the prefix does not force unavailable standard headers in constrained builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/cxx.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/cxx.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/cxx.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_CXX`. Other relevant macros in this header include `BOOST_LIB_STD_CXX`, `BOOST_LIB_STD_CXX_AVAILABLE`, `BOOST_LIB_STD_CXX_NAME`. Display-name macros are `BOOST_LIB_STD_CXX_NAME` "libc++". Predef test registrations are `BOOST_LIB_STD_CXX,BOOST_LIB_STD_CXX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_LIBCPP_VERSION`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/cxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/dinkumware.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/dinkumware.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/dinkumware.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_DINKUMWARE`. Other relevant macros in this header include `BOOST_LIB_STD_DINKUMWARE`, `BOOST_LIB_STD_DINKUMWARE_AVAILABLE`, `BOOST_LIB_STD_DINKUMWARE_NAME`. Display-name macros are `BOOST_LIB_STD_DINKUMWARE_NAME` "Dinkumware". Predef test registrations are `BOOST_LIB_STD_DINKUMWARE,BOOST_LIB_STD_DINKUMWARE_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_YVALS`, `__IBMCPP__`, `_CPPLIB_VER`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/dinkumware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/libcomo.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/libcomo.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/libcomo.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_COMO`. Other relevant macros in this header include `BOOST_LIB_STD_COMO`, `BOOST_LIB_STD_COMO_AVAILABLE`, `BOOST_LIB_STD_COMO_NAME`. Display-name macros are `BOOST_LIB_STD_COMO_NAME` "Comeau Computing". Predef test registrations are `BOOST_LIB_STD_COMO,BOOST_LIB_STD_COMO_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__LIBCOMO__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/libcomo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/modena.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/modena.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/modena.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_MSIPL`. Other relevant macros in this header include `BOOST_LIB_STD_MSIPL`, `BOOST_LIB_STD_MSIPL_AVAILABLE`, `BOOST_LIB_STD_MSIPL_NAME`. Display-name macros are `BOOST_LIB_STD_MSIPL_NAME` "Modena Software Lib++". Predef test registrations are `BOOST_LIB_STD_MSIPL,BOOST_LIB_STD_MSIPL_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `MSIPL_COMPILE_H`, `__MSIPL_COMPILE_H`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/modena.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msl.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msl.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msl.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_MSL`. Other relevant macros in this header include `BOOST_LIB_STD_MSL`, `BOOST_LIB_STD_MSL_AVAILABLE`, `BOOST_LIB_STD_MSL_NAME`. Display-name macros are `BOOST_LIB_STD_MSL_NAME` "Metrowerks". Predef test registrations are `BOOST_LIB_STD_MSL,BOOST_LIB_STD_MSL_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__MSL_CPP__`, `__MSL__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msvc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msvc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msvc.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_MSVC`. Other relevant macros in this header include `BOOST_LIB_STD_MSVC`, `BOOST_LIB_STD_MSVC_AVAILABLE`, `BOOST_LIB_STD_MSVC_NAME`. Display-name macros are `BOOST_LIB_STD_MSVC_NAME` "Microsoft stdlib". Predef test registrations are `BOOST_LIB_STD_MSVC, BOOST_LIB_STD_MSVC_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `_MSVC_STL_VERSION`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/msvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/roguewave.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/roguewave.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/roguewave.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_RW`. Other relevant macros in this header include `BOOST_LIB_STD_RW`, `BOOST_LIB_STD_RW_AVAILABLE`, `BOOST_LIB_STD_RW_NAME`. Display-name macros are `BOOST_LIB_STD_RW_NAME` "Roguewave". Predef test registrations are `BOOST_LIB_STD_RW,BOOST_LIB_STD_RW_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__STD_RWCOMPILER_H__`, `_RWSTD_VER`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/roguewave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/sgi.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/sgi.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/sgi.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_SGI`. Other relevant macros in this header include `BOOST_LIB_STD_SGI`, `BOOST_LIB_STD_SGI_AVAILABLE`, `BOOST_LIB_STD_SGI_NAME`. Display-name macros are `BOOST_LIB_STD_SGI_NAME` "SGI". Predef test registrations are `BOOST_LIB_STD_SGI,BOOST_LIB_STD_SGI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__STL_CONFIG_H`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/sgi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stdcpp3.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stdcpp3.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stdcpp3.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_GNU`. Other relevant macros in this header include `BOOST_LIB_STD_GNU`, `BOOST_LIB_STD_GNU_AVAILABLE`, `BOOST_LIB_STD_GNU_NAME`. Display-name macros are `BOOST_LIB_STD_GNU_NAME` "GNU". Predef test registrations are `BOOST_LIB_STD_GNU,BOOST_LIB_STD_GNU_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__GLIBCPP__`, `__GLIBCXX__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stdcpp3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stlport.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stlport.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stlport.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_STLPORT`. Other relevant macros in this header include `BOOST_LIB_STD_STLPORT`, `BOOST_LIB_STD_STLPORT_AVAILABLE`, `BOOST_LIB_STD_STLPORT_NAME`. Display-name macros are `BOOST_LIB_STD_STLPORT_NAME` "STLport". Predef test registrations are `BOOST_LIB_STD_STLPORT,BOOST_LIB_STD_STLPORT_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__SGI_STL_PORT`, `_STLPORT_VERSION`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/stlport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/vacpp.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/vacpp.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/vacpp.h` is a Boost.Predef C++ standard library detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_LIB_STD_IBM`. Other relevant macros in this header include `BOOST_LIB_STD_IBM`, `BOOST_LIB_STD_IBM_AVAILABLE`, `BOOST_LIB_STD_IBM_NAME`. Display-name macros are `BOOST_LIB_STD_IBM_NAME` "IBM VACPP". Predef test registrations are `BOOST_LIB_STD_IBM,BOOST_LIB_STD_IBM_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as `__IBMCPP__`, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/library/std/_prefix.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/vacpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/make.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/make.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/make.h` defines the Boost.Predef version-conversion macro library. Vendor predefined macros often encode versions as packed decimal, packed hexadecimal, or dates; this header normalizes those encodings into `BOOST_VERSION_NUMBER(major, minor, patch)` values.

## Important APIs, Types, and Functions

The public surface is the `BOOST_PREDEF_MAKE_*` macro family. This file defines 31 conversion macros, including `BOOST_PREDEF_MAKE_0X_VRP(V) BOOST_VERSION_NUMBER((V&0xF00)>>8,(V&0xF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VVRP(V) BOOST_VERSION_NUMBER((V&0xFF00)>>8,(V&0xF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VRPP(V) BOOST_VERSION_NUMBER((V&0xF000)>>12,(V&0xF00)>>8,(V&0xFF))`, `BOOST_PREDEF_MAKE_0X_VVRR(V) BOOST_VERSION_NUMBER((V&0xFF00)>>8,(V&0xFF),0)`, `BOOST_PREDEF_MAKE_0X_VRRPPPP(V) BOOST_VERSION_NUMBER((V&0xF000000)>>24,(V&0xFF0000)>>16,(V&0xFFFF))`, `BOOST_PREDEF_MAKE_0X_VVRRP(V) BOOST_VERSION_NUMBER((V&0xFF000)>>12,(V&0xFF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VRRPP000(V) BOOST_VERSION_NUMBER((V&0xF0000000)>>28,(V&0xFF00000)>>20,(V&0xFF000)>>12)`, `BOOST_PREDEF_MAKE_0X_VVRRPP(V) BOOST_VERSION_NUMBER((V&0xFF0000)>>16,(V&0xFF00)>>8,(V&0xFF))`, `BOOST_PREDEF_MAKE_10_VPPP(V) BOOST_VERSION_NUMBER(((V)/1000)%10,0,(V)%1000)`, `BOOST_PREDEF_MAKE_10_VVPPP(V) BOOST_VERSION_NUMBER(((V)/1000)%100,0,(V)%1000)`, `BOOST_PREDEF_MAKE_10_VR0(V) BOOST_VERSION_NUMBER(((V)/100)%10,((V)/10)%10,0)`, `BOOST_PREDEF_MAKE_10_VRP(V) BOOST_VERSION_NUMBER(((V)/100)%10,((V)/10)%10,(V)%10)`, `BOOST_PREDEF_MAKE_10_VRP000(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/10000)%10,((V)/1000)%10)`, `BOOST_PREDEF_MAKE_10_VRPPPP(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/10000)%10,(V)%10000)`, `BOOST_PREDEF_MAKE_10_VRPP(V) BOOST_VERSION_NUMBER(((V)/1000)%10,((V)/100)%10,(V)%100)`, `BOOST_PREDEF_MAKE_10_VRR(V) BOOST_VERSION_NUMBER(((V)/100)%10,(V)%100,0)`, `BOOST_PREDEF_MAKE_10_VRRPP(V) BOOST_VERSION_NUMBER(((V)/10000)%10,((V)/100)%100,(V)%100)`, `BOOST_PREDEF_MAKE_10_VRR000(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/1000)%100,0)`. Date helpers include `BOOST_PREDEF_MAKE_DATE`, `BOOST_PREDEF_MAKE_YYYYMMDD`, `BOOST_PREDEF_MAKE_YYYY`, and `BOOST_PREDEF_MAKE_YYYYMM`. Direct includes are `boost/predef/detail/test.h`.

## Control Flow

There is no branching detection logic. Each macro applies integer division, modulo, or bit masking/shifting to decompose a vendor value and recompose it with `BOOST_VERSION_NUMBER`. Date macros store years relative to the 1970 epoch used by Boost.Predef version numbering.

## State and Persistence Behavior

The header is preprocessor-only. It stores no runtime state and has no side effects other than making conversion macros available in the current translation unit.

## Dependencies and Integration Points

Nearly every concrete Predef detector depends on this file when its vendor macro carries a structured version. Compiler, OS, architecture, language, and library headers call these macros to keep their `BOOST_*` values comparable.

## Risks and Edge Cases

A wrong conversion format silently reports an incorrect version while still marking the feature available. Date conversion intentionally defaults missing month/day values to January 1. Packed macro arithmetic assumes the vendor value is numeric and available to the preprocessor.

## Test Signals

Unit preprocessor tests should feed representative hexadecimal, decimal, and date values into each conversion macro and compare the result with expected `BOOST_VERSION_NUMBER` values. Detector-specific tests indirectly cover the macros by checking known compiler/library version macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/make.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os.h` is a umbrella operating-system include that aggregates AIX, AmigaOS, BeOS, BSD family, Cygwin, Haiku, HP-UX, IRIX, iOS, Linux, macOS, OS/400, QNX, Solaris, Unix, VMS, and Windows detectors. It is an aggregation header: its job is to include the concrete detector headers in a stable order rather than to perform substantial detection itself.

## Important APIs, Types, and Functions

The header exports the macros provided by its direct includes. Direct includes are `boost/predef/os/aix.h`, `boost/predef/os/amigaos.h`, `boost/predef/os/beos.h`, `boost/predef/os/bsd.h`, `boost/predef/os/cygwin.h`, `boost/predef/os/haiku.h`, `boost/predef/os/hpux.h`, `boost/predef/os/irix.h`, `boost/predef/os/ios.h`, `boost/predef/os/linux.h`, `boost/predef/os/macos.h`, `boost/predef/os/os400.h`, `boost/predef/os/qnxnto.h`, `boost/predef/os/solaris.h`, `boost/predef/os/unix.h`, `boost/predef/os/vms.h`, `boost/predef/os/windows.h`. Consumers normally include this file when they want the whole `os.h` detection family instead of selecting an individual detector.

## Control Flow

Preprocessor control flow is include-driven. The include guard prevents repeated expansion, then each listed child header runs its own detection logic, defines a `BOOST_*` version macro, optionally defines an `*_AVAILABLE` marker, and registers Boost.Predef tests.

## State and Persistence Behavior

There is no runtime state or persistence. The only state is the set of preprocessor macros produced during translation of the including source file.

## Dependencies and Integration Points

This header is part of the vendored Boost.Predef tree consumed by mergerfs through vendored Boost headers. It integrates by making platform/compiler/OS facts available to conditional compilation paths without requiring external Boost installation.

## Risks and Edge Cases

Aggregation order matters for detectors that emulate another compiler or operating system. Removing or reordering includes can change which macro becomes primary. Because this is vendored code, partial updates can leave an umbrella header pointing at missing or incompatible child headers.

## Test Signals

Compile a small translation unit that includes `sources/user-network-fs/mergerfs/vendored/boost/predef/os.h` and checks expected `BOOST_*` macros under representative host toolchains. The Boost.Predef `BOOST_PREDEF_DECLARE_TEST` registrations in child headers are also useful upstream signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/aix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/aix.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/aix.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_AIX`. Other relevant macros in this header include `BOOST_OS_AIX`, `BOOST_OS_AIX_AVAILABLE`, `BOOST_OS_AIX_NAME`. Display-name macros are `BOOST_OS_AIX_NAME` "IBM AIX". Predef test registrations are `BOOST_OS_AIX,BOOST_OS_AIX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/aix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/amigaos.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/amigaos.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/amigaos.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_AMIGAOS`. Other relevant macros in this header include `BOOST_OS_AMIGAOS`, `BOOST_OS_AMIGAOS_AVAILABLE`, `BOOST_OS_AMIGAOS_NAME`. Display-name macros are `BOOST_OS_AMIGAOS_NAME` "AmigaOS". Predef test registrations are `BOOST_OS_AMIGAOS,BOOST_OS_AMIGAOS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/amigaos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/beos.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/beos.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/beos.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BEOS`. Other relevant macros in this header include `BOOST_OS_BEOS`, `BOOST_OS_BEOS_AVAILABLE`, `BOOST_OS_BEOS_NAME`. Display-name macros are `BOOST_OS_BEOS_NAME` "BeOS". Predef test registrations are `BOOST_OS_BEOS,BOOST_OS_BEOS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/beos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD`. Other relevant macros in this header include `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_BSD_NAME`. Display-name macros are `BOOST_OS_BSD_NAME` "BSD". Predef test registrations are `BOOST_OS_BSD,BOOST_OS_BSD_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/macos.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/os/bsd/bsdi.h`, `boost/predef/os/bsd/dragonfly.h`, `boost/predef/os/bsd/free.h`, `boost/predef/os/bsd/open.h`, `boost/predef/os/bsd/net.h`, `sys/param.h`, `boost/predef/detail/os_detected.h`, `boost/predef/os/bsd/bsdi.h`, `boost/predef/os/bsd/dragonfly.h`, `boost/predef/os/bsd/free.h`, `boost/predef/os/bsd/open.h`, `boost/predef/os/bsd/net.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/bsdi.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/bsdi.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/bsdi.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD_BSDI`, `BOOST_OS_BSD`. Other relevant macros in this header include `BOOST_OS_BSD_BSDI`, `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_BSD_BSDI_AVAILABLE`, `BOOST_OS_BSD_BSDI_NAME`. Display-name macros are `BOOST_OS_BSD_BSDI_NAME` "BSDi BSD/OS". Predef test registrations are `BOOST_OS_BSD_BSDI,BOOST_OS_BSD_BSDI_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/bsd.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/bsdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/dragonfly.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/dragonfly.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/dragonfly.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD_DRAGONFLY`, `BOOST_OS_BSD`, `BOOST_OS_DRAGONFLY_BSD`. Other relevant macros in this header include `BOOST_OS_BSD_DRAGONFLY`, `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_DRAGONFLY_BSD`, `BOOST_OS_BSD_DRAGONFLY_AVAILABLE`, `BOOST_OS_BSD_DRAGONFLY_NAME`. Display-name macros are `BOOST_OS_BSD_DRAGONFLY_NAME` "DragonFly BSD". Predef test registrations are `BOOST_OS_BSD_DRAGONFLY,BOOST_OS_BSD_DRAGONFLY_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/bsd.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/dragonfly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/free.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/free.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/free.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD_FREE`, `BOOST_OS_BSD`. Other relevant macros in this header include `BOOST_OS_BSD_FREE`, `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_BSD_FREE_AVAILABLE`, `BOOST_OS_BSD_FREE_NAME`. Display-name macros are `BOOST_OS_BSD_FREE_NAME` "Free BSD". Predef test registrations are `BOOST_OS_BSD_FREE,BOOST_OS_BSD_FREE_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/bsd.h`, `sys/param.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/free.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/net.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/net.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/net.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD_NET`, `BOOST_OS_BSD`. Other relevant macros in this header include `BOOST_OS_BSD_NET`, `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_BSD_NET_AVAILABLE`, `BOOST_OS_BSD_NET_NAME`. Display-name macros are `BOOST_OS_BSD_NET_NAME` "NetBSD". Predef test registrations are `BOOST_OS_BSD_NET,BOOST_OS_BSD_NET_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/bsd.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/open.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/open.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/open.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_BSD_OPEN`, `BOOST_OS_BSD`. Other relevant macros in this header include `BOOST_OS_BSD_OPEN`, `BOOST_OS_BSD`, `BOOST_OS_BSD_AVAILABLE`, `BOOST_OS_BSD_OPEN_AVAILABLE`, `BOOST_OS_BSD_OPEN_NAME`. Display-name macros are `BOOST_OS_BSD_OPEN_NAME` "OpenBSD". Predef test registrations are `BOOST_OS_BSD_OPEN,BOOST_OS_BSD_OPEN_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/bsd.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/bsd/open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/cygwin.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/cygwin.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/cygwin.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_CYGWIN`. Other relevant macros in this header include `BOOST_OS_CYGWIN`, `BOOST_OS_CYGWIN_AVAILABLE`, `BOOST_OS_CYGWIN_NAME`. Display-name macros are `BOOST_OS_CYGWIN_NAME` "Cygwin". Predef test registrations are `BOOST_OS_CYGWIN,BOOST_OS_CYGWIN_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `cygwin/version.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/cygwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/haiku.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/haiku.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/haiku.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_HAIKU`. Other relevant macros in this header include `BOOST_OS_HAIKU`, `BOOST_OS_HAIKU_AVAILABLE`, `BOOST_OS_HAIKU_NAME`. Display-name macros are `BOOST_OS_HAIKU_NAME` "Haiku". Predef test registrations are `BOOST_OS_HAIKU,BOOST_OS_HAIKU_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/haiku.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/hpux.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/hpux.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/hpux.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_HPUX`. Other relevant macros in this header include `BOOST_OS_HPUX`, `BOOST_OS_HPUX_AVAILABLE`, `BOOST_OS_HPUX_NAME`. Display-name macros are `BOOST_OS_HPUX_NAME` "HP-UX". Predef test registrations are `BOOST_OS_HPUX,BOOST_OS_HPUX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/hpux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/ios.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/ios.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/ios.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_IOS`. Other relevant macros in this header include `BOOST_OS_IOS`, `BOOST_OS_IOS_AVAILABLE`, `BOOST_OS_IOS_NAME`. Display-name macros are `BOOST_OS_IOS_NAME` "iOS". Predef test registrations are `BOOST_OS_IOS,BOOST_OS_IOS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/ios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/irix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/irix.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/irix.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_IRIX`. Other relevant macros in this header include `BOOST_OS_IRIX`, `BOOST_OS_IRIX_AVAILABLE`, `BOOST_OS_IRIX_NAME`. Display-name macros are `BOOST_OS_IRIX_NAME` "IRIX". Predef test registrations are `BOOST_OS_IRIX,BOOST_OS_IRIX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/irix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/linux.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/linux.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/linux.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_LINUX`. Other relevant macros in this header include `BOOST_OS_LINUX`, `BOOST_OS_LINUX_AVAILABLE`, `BOOST_OS_LINUX_NAME`. Display-name macros are `BOOST_OS_LINUX_NAME` "Linux". Predef test registrations are `BOOST_OS_LINUX,BOOST_OS_LINUX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/macos.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/macos.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/macos.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_MACOS`. Other relevant macros in this header include `BOOST_OS_MACOS`, `BOOST_OS_MACOS_AVAILABLE`, `BOOST_OS_MACOS_NAME`. Display-name macros are `BOOST_OS_MACOS_NAME` "Mac OS". Predef test registrations are `BOOST_OS_MACOS,BOOST_OS_MACOS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/os/ios.h`, `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/macos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/os400.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/os400.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/os400.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_OS400`. Other relevant macros in this header include `BOOST_OS_OS400`, `BOOST_OS_OS400_AVAILABLE`, `BOOST_OS_OS400_NAME`. Display-name macros are `BOOST_OS_OS400_NAME` "IBM OS/400". Predef test registrations are `BOOST_OS_OS400,BOOST_OS_OS400_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/os400.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/qnxnto.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/qnxnto.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/qnxnto.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_QNX`. Other relevant macros in this header include `BOOST_OS_QNX`, `BOOST_OS_QNX_AVAILABLE`, `BOOST_OS_QNX_NAME`. Display-name macros are `BOOST_OS_QNX_NAME` "QNX". Predef test registrations are `BOOST_OS_QNX,BOOST_OS_QNX_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/qnxnto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/solaris.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/os/solaris.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/os/solaris.h` is a Boost.Predef operating system detector. It reports availability and version information through `BOOST_*` preprocessor macros so code can select platform-specific branches at compile time.

## Important APIs, Types, and Functions

Primary detection macros are `BOOST_OS_SOLARIS`. Other relevant macros in this header include `BOOST_OS_SOLARIS`, `BOOST_OS_SOLARIS_AVAILABLE`, `BOOST_OS_SOLARIS_NAME`. Display-name macros are `BOOST_OS_SOLARIS_NAME` "Solaris". Predef test registrations are `BOOST_OS_SOLARIS,BOOST_OS_SOLARIS_NAME`.

## Control Flow

The file starts each primary macro at `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, checks vendor/compiler symbols such as none, and upgrades the macro to either a parsed `BOOST_VERSION_NUMBER(...)` value or `BOOST_VERSION_NUMBER_AVAILABLE`. When detection succeeds it defines an `*_AVAILABLE` marker and, for this family, runs any sentinel include needed by Boost.Predef. OS detectors include `boost/predef/detail/os_detected.h` when they claim a primary OS, preventing later mutually exclusive OS headers from also becoming primary.

## State and Persistence Behavior

There is no runtime state. The detector mutates only preprocessor macro state in the current translation unit. Results are not cached outside compilation and can differ across target triples, compiler flags, SDK headers, and language modes.

## Dependencies and Integration Points

Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/os_detected.h`, `boost/predef/detail/test.h`. The detector is reached through its family aggregate header and often through `boost/predef.h`. Mergerfs carries this as vendored Boost infrastructure, so build portability depends on these macros matching the active toolchain and target environment.

## Risks and Edge Cases

Predefined vendor macros are not perfectly standardized. Cross-compilers may emulate another compiler or expose host and target symbols together. Version parsing must match each vendor encoding exactly, and broad fallback branches can mark a platform available without a precise version. Include order matters for primary-versus-emulated compiler and OS detection.

## Test Signals

Useful tests are compile-time probes under representative compilers, OS targets, and cross-compilation settings that assert the primary macro, `*_AVAILABLE` marker, and parsed version. The registered Boost.Predef test macro at the bottom of the file is the upstream self-test hook.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/os/solaris.h -->
