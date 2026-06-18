# sources/distributed-fs/lizardfs/src/common/flat_set.h

Purpose: implements a sorted vector-backed set with `std::set`-like API and better memory locality for small collections.

Important APIs/types/functions: template `flat_set<T,C,Compare>` privately inherits comparator for EBO. It provides constructors including sorted/trusted input, assignment, iterators, `data`, capacity, `reserve`, insert with optional hint, range insert, erase, lookup, equal range, comparators, relational operators, and `swap`.

Control flow: normal inserts lower-bound and insert only if no equivalent value exists. Hint inserts check neighboring values to insert in O(1) when the hint is valid, otherwise search a narrowed range. Range/initializer inserts reserve once and insert each element.

State and persistence: in-memory vector-like storage. No persistence or synchronization. Iterators are invalidated by underlying container mutations.

Dependencies and integration: depends on standard algorithms and containers. Used by `flat_map`, `Goal` slice containers, and other common structures.

Risks: O(n) insertion/erase, trusted sorted construction can store duplicates or unsorted data if caller lies, and `swap` implemented as `std::swap(*this, other)` may recurse into ADL/swap patterns depending on overload resolution though tests cover basic use.

Test signals: `flat_set_unittest.cc` covers redundant inserts, hint insert, range insert, equal range, iterators, swap, erase, constructors, and assignment.
