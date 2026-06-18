# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 12680-18782

## Scope

This chunk covers the generated value-parameter support in the fused Google Test 1.8.1 header embedded under RocksDB. It starts in the tail of `internal::ValueArray15`, continues through `internal::ValueArray16` through `internal::ValueArray50`, defines the generated Cartesian-product generator and holder classes used by `Combine()`, closes `gtest-param-util-generated.h`, and then begins the public parameter-generator factory functions in namespace `testing`.

The public factory section includes `Range()`, all `ValuesIn()` overloads, generated `Values()` overloads for 1 through 50 arguments, `Bool()`, and the beginning of `Combine()` overloads. The chunk ends on the return type for the public four-argument `Combine()` overload, so later `Combine()` overload bodies and the remainder of the header are outside this chunk.

## Purpose

- Provide source-level implementations for Google Test value-parameterized test generator helpers in the fused single-header distribution used by RocksDB's vendored test dependency.
- Let users write `Values(...)` with heterogeneous literal arguments and defer conversion until the expression is assigned to a concrete `ParamGenerator<T>`.
- Let users build `ParamGenerator<T>` instances from ranges, C arrays, STL containers, and iterator ranges.
- Let users generate Boolean parameter sequences with `Bool()`.
- When `GTEST_HAS_COMBINE` is enabled, let users combine two to ten parameter generators into a Cartesian product whose element type is `testing::tuple<T1, ..., TN>`.
- Avoid variadic templates by using generated fixed-arity classes and overloads, which keeps Google Test 1.8.1 compatible with older C++ compilers.

## Important APIs, Types, And Functions

- `internal::ValueArray15` through `internal::ValueArray50` are generated holder classes for the high-arity `Values()` implementation. Each stores constructor arguments in `const Tn vn_` members, supports copy construction, disables assignment by declaring a private unimplemented `operator=`, and exposes `template <typename T> operator ParamGenerator<T>() const`.
- Each `ValueArrayN::operator ParamGenerator<T>()` builds a local `const T array[]` by `static_cast<T>`-converting every stored value, then delegates to `ValuesIn(array)`. This gives `Values(1, 2, 3.5)` the ability to become a `ParamGenerator<double>`, `ParamGenerator<int>`, or another compatible target selected by the test fixture parameter type.
- `testing::Range(T start, T end, IncrementT step)` constructs `internal::RangeGenerator<T, IncrementT>`. The two-argument overload delegates to `Range(start, end, 1)`.
- `testing::ValuesIn(ForwardIterator begin, ForwardIterator end)` determines the parameter type with `internal::IteratorTraits<ForwardIterator>::value_type` and constructs `internal::ValuesInIteratorRangeGenerator<ParamType>`.
- `testing::ValuesIn(const T (&array)[N])` forwards to the iterator overload with `array` and `array + N`.
- `testing::ValuesIn(const Container& container)` forwards to the iterator overload with `container.begin()` and `container.end()`.
- `testing::Values()` overloads for arities 1 through 50 return the corresponding `internal::ValueArrayN<...>` holder. In this chunk, the source-visible overload list includes all arities and the high-arity tail from 15 through 50 aligns with the generated classes above.
- `testing::Bool()` is a convenience wrapper returning `Values(false, true)` as `internal::ParamGenerator<bool>`.
- `internal::CartesianProductGenerator2` through `internal::CartesianProductGenerator10` implement the concrete generator interfaces for `Combine()`. Each derives from `ParamGeneratorInterface<testing::tuple<...> >`, stores its input `ParamGenerator<Tn>` objects by value, and creates nested iterators from each input generator's begin/end positions.
- Each nested Cartesian `Iterator` implements `ParamIteratorInterface<ParamType>` methods: `BaseGenerator()`, `Advance()`, `Clone()`, `Current()`, and `Equals()`.
- `internal::CartesianProductHolder2` through `internal::CartesianProductHolder10` are polymorphic adapter holders returned by public `Combine()` overloads. They store the original generator expressions by value and convert later to `ParamGenerator<testing::tuple<T...> >` by statically converting each held expression to `ParamGenerator<Tn>` and allocating the matching `CartesianProductGeneratorN`.
- Public `testing::Combine()` overloads begin in this chunk. The two- and three-argument overloads are fully present, and the four-argument overload declaration begins at the chunk boundary.

## Control Flow

`Values(...)` is intentionally two-stage. A call such as `Values("a", "b")` returns a `ValueArray2<const char*, const char*>`, not an immediate concrete parameter generator. When Google Test instantiation needs a `ParamGenerator<T>`, the holder conversion operator runs, casts every saved value to `T`, places those converted values in a stack array, and calls `ValuesIn(array)`. `ValuesIn()` immediately constructs a `ValuesInIteratorRangeGenerator`, whose implementation elsewhere copies the values, so the local stack array is not retained after conversion.

`Range()` is direct: the public helper creates a `RangeGenerator` with the caller's start, end, and step. The generated sequence is documented as half-open and requires `start < end` for non-empty output. Runtime iteration logic for `RangeGenerator` lives earlier in the header, outside this chunk.

`ValuesIn()` overloads normalize three input styles into a begin/end iterator pair. The iterator overload deduces the value type and constructs a generator around the supplied range. The array overload uses pointer iterators, and the container overload uses STL-style iterators. The surrounding comments explicitly state that values are copied for use later during `RUN_ALL_TESTS()`.

When `GTEST_HAS_COMBINE` is enabled, `Combine(g1, g2, ...)` returns a `CartesianProductHolderN` expression. Like `Values()`, this holder is not the final typed generator. Its conversion operator selects tuple element types from the consuming context, converts each stored expression to `ParamGenerator<Tn>`, and allocates a `CartesianProductGeneratorN<T...>`.

Each `CartesianProductGeneratorN::Begin()` constructs an iterator with every component at its begin position. `End()` constructs one with every component at end. The nested iterator caches each component's `begin`, `end`, and current iterator. `Advance()` increments the last component first; when that component reaches end, it resets that component to begin and increments the previous component. This carry propagation repeats toward the first component, producing lexicographic Cartesian-product order with the rightmost generator varying fastest.

`ComputeCurrentValue()` materializes the current tuple in a `linked_ptr<ParamType>` whenever the iterator is not at end. `AtEnd()` returns true if any component iterator equals its corresponding end iterator. This is important for empty inputs: a Cartesian product with any empty component is immediately empty, and all exhausted combinations compare as end even if individual component states differ.

`Equals()` first checks that both iterators came from the same base generator pointer using `GTEST_CHECK_`. It then downcasts with `CheckedDowncastToActualType` and reports equality if both are logically at end or if every component current iterator is equal. This prevents accidental comparison between unrelated generator instances while still treating multiple exhausted states as the same end position.

## State And Persistence Behavior

This code does not persist RocksDB state and does not interact with RocksDB storage. It is part of the vendored test framework and affects only in-memory test registration and parameter generation.

The relevant state is test-generation state:

- `ValueArrayN` holders store copies of all `Values()` arguments as `const` members until conversion to a concrete `ParamGenerator<T>`.
- `ValuesIn()` generators copy range elements for later test execution, decoupling test parameters from temporary containers or stack arrays used during instantiation.
- `CartesianProductGeneratorN` stores input `ParamGenerator<Tn>` objects by value. Those generators own or share their own generator implementation objects according to Google Test's `ParamGenerator` wrapper semantics.
- Cartesian iterators store begin/end/current iterators for every input generator and a heap-allocated current tuple through `linked_ptr`. Cloned iterators recompute the tuple from copied component iterator positions.
- All generated holder and generator classes disable assignment, avoiding accidental member reassignment while still permitting copy construction where needed for expression passing and iterator cloning.

## Dependencies And Integration Points

- This chunk is inside `namespace testing` and `namespace testing::internal`, and depends on parameter-generator infrastructure defined earlier in `gtest.h`: `ParamGenerator`, `ParamGeneratorInterface`, `ParamIteratorInterface`, `RangeGenerator`, `ValuesInIteratorRangeGenerator`, `IteratorTraits`, and `linked_ptr`.
- Tuple support comes from Google Test's tuple implementation exposed as `testing::tuple`. `Combine()` is limited to ten inputs because this Google Test release's tuple implementation has that generated arity limit.
- Error checking and RTTI-like downcasting use internal helpers/macros including `GTEST_CHECK_` and `CheckedDowncastToActualType`.
- The entire Cartesian-product section and public `Combine()` helpers are guarded by `GTEST_HAS_COMBINE`. Builds without that feature still provide `Range()`, `ValuesIn()`, `Values()`, and `Bool()`.
- Public integration is through parameterized-test macros elsewhere in Google Test, especially `TEST_P`, `TestWithParam<T>`, and `INSTANTIATE_TEST_CASE_P`, which accept these generator expressions and convert them to typed `ParamGenerator<T>` objects.
- RocksDB integrates this only as a vendored third-party testing dependency. Production RocksDB storage-engine code should not depend on these APIs.

## Risks And Edge Cases

- This is generated, pre-variadic-template code. Any manual patch to one arity can leave other arities inconsistent, especially across `ValueArrayN`, `Values()` overloads, `CartesianProductGeneratorN`, `CartesianProductHolderN`, and `Combine()` overloads.
- `Values()` conversion uses `static_cast<T>` for every argument. Narrowing, lossy floating-point conversion, pointer conversion, or user-defined conversion side effects happen at generator conversion time, not at the original `Values()` call site.
- `ValueArrayN` stores values by value. Expensive objects are copied, and non-copyable argument types are not supported by this generated API shape.
- `ValuesIn(const Container&)` assumes the container has `value_type`, `begin()`, and `end()` members. It also relies on the range-copy behavior of `ValuesInIteratorRangeGenerator`; if that contract were changed, temporary containers passed to `ValuesIn(GetVector())` would become dangerous.
- Cartesian products grow multiplicatively. Large input generators can produce very large numbers of instantiated tests, increasing registration time, binary/test metadata size, and runtime.
- Empty component generators make the whole Cartesian product empty because `AtEnd()` checks every component. This is correct but can silently result in no parameterized tests for a suite if one input sequence is empty.
- `Advance()` asserts that the iterator is not already at end. Calling it on an exhausted iterator is a contract violation and would be caught only in assertion-enabled builds.
- `Equals()` aborts via `GTEST_CHECK_` if iterators from different base generators are compared. This is intentional but can surprise code that treats parameter iterators like ordinary STL iterators.
- The generated Cartesian iterators allocate a new tuple object each time `ComputeCurrentValue()` runs. Very large products can therefore allocate heavily during parameter enumeration.
- The chunk boundary cuts through public `Combine()` overload declarations. A source audit or patch touching `Combine()` must include the following chunk before drawing conclusions about all public arities.

## Test Signals

- Parameterized tests should confirm `Values()` supports representative low and high arities, including the generated high-arity range up to 50 arguments.
- Type-conversion tests should instantiate fixtures where `Values()` contains heterogeneous values and the fixture parameter type controls the final conversion.
- Lifetime tests should pass temporary arrays/containers/ranges through `ValuesIn()` and verify values remain available during `RUN_ALL_TESTS()`.
- `Range()` tests should cover half-open behavior, custom increments, floating-point or user-defined increment types, and empty ranges when `start < end` is false.
- `Bool()` tests should verify the generated sequence is exactly `false` followed by `true`.
- `Combine()` tests under `GTEST_HAS_COMBINE` should verify Cartesian order, especially that the rightmost generator varies fastest.
- Empty-product tests should combine non-empty generators with one empty generator and verify no parameter values are produced.
- Iterator tests should cover begin/end equality, cloned iterator equality, and exhaustion behavior where different component iterator states still compare as logical end.
- Negative tests or death tests can cover comparing iterators from different generator instances, which should trigger the `GTEST_CHECK_` path.
- Build tests should cover configurations with `GTEST_HAS_COMBINE` enabled and disabled, since the public API surface changes under that macro.
