# sources/distributed-fs/lizardfs/src/common/counting_sort.h

Purpose: implements stable counting-sort helpers for integer-keyed ranges with small-vector-backed count/index storage.

Important APIs/types/functions: `counting_sort_copy(first,last,output,get_key)` builds prefix counts and writes sorted elements into `output`. `counting_sort(OutputIterator first,last,get_key)` intends to sort a range in place. `counting_sort(DataContainer&,get_key)` sorts a vector-like container by creating a same-sized result.

Control flow: `counting_sort_copy` resizes an index array to `max_key + 2`, accumulates counts shifted by one, prefix-sums them, then moves each input into `output[element_index[key]++]`, preserving relative order for equal keys.

State and persistence: temporary in-memory index vector and result storage only.

Dependencies and integration: depends on `small_vector.h` and iterator traits. It is useful for bounded non-negative key domains in planning and scheduling code.

Risks: keys are assumed non-negative and reasonably bounded after conversion to `std::size_t`; huge keys can allocate huge index vectors. The iterator overload appears defective: after sorting into `result`, it calls `std::copy(first, last, result.begin())`, which copies the original range into the result buffer rather than copying `result` back to `first`. The container overload uses the copy helper directly and assigns `data = std::move(result)`.

Test signals: `counting_sort_unittest.cc` covers only `counting_sort_copy`, including stability; it does not catch the in-place iterator overload issue.
