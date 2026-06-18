## sources/distributed-fs/lizardfs/src/mount/tweaks.cc

Purpose: implements runtime tweak registry for selected atomic variables, exposed through the tweaks special file.

Important APIs/types: abstract `Variable` supports string set/get. `VariableImpl<T>` wraps `std::atomic<T>`, parses values with `std::boolalpha`, and stores only on successful stream extraction. `Tweaks::registerVariable` overloads accept atomic bool, uint32_t, and uint64_t. `setValue` applies to all variables with matching name; `getAllValues` returns tab-separated name/value lines. Defines global `Tweaks gTweaks`.

State and dependencies: registry is a list of name/unique_ptr pairs in `Tweaks::Impl`. No explicit mutex protects registration or set/get; expected use is mostly during initialization plus special-file writes.

Risks: duplicate names are allowed and all are set. Parsing accepts prefixes such as `16 xxx`, as confirmed by tests. There is no feedback for unknown names or invalid values. Concurrent access is not synchronized around the registry.

Test signals: `tweaks_unittest.cc` covers output formatting, invalid numeric input ignored, partial numeric parses accepted, newline handling, and bool parsing.
