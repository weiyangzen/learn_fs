# Research Group subset-b-009671

Grouped source research for mergerfs policy helpers, runtime utility headers, process state helpers, and Python POSIX parity tests. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lup.hpp -->
# sources/user-network-fs/mergerfs/src/policy_lup.hpp

## Purpose
Declares the `Policy::LUP` policy family for mergerfs operation routing. The policy name is `lup`, representing the least-used path-preserving selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lup.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lus.cpp -->
# sources/user-network-fs/mergerfs/src/policy_lus.cpp

## Purpose
Implements the `lus` create policy, choosing the writable branch with the least used space among all eligible branches. Action and search behavior delegates to existing-path `eplus` helpers.

## Important APIs, Types, and Functions
The private `_create()` scans `Branches`, calls `fs::info()`, checks `Branch::ro_or_nc()`, `info.readonly`, and `Branch::minfreespace()`, then appends the branch with the smallest `info.spaceused`. `Policy::LUS::{Action,Create,Search}::operator()` expose the policy interface.

## Control Flow
Create starts with `ENOENT` as the fallback error, filters read-only, no-create, missing/stat-failed, and low-space branches, and keeps the best branch by `spaceused`. If no branch survives, it returns the most relevant negative errno. Action/search call `Policies::Action::eplus()` and `Policies::Search::eplus()`.

## State and Persistence Behavior
The function keeps only local scan state. Persistent effects happen in callers that use the selected branch to create files or route operations.

## Dependencies and Integration Points
It integrates with `fs_info`, `policy_error`, `Branches`, and the shared `Policies::*::eplus` existing-path strategy.

## Risks and Edge Cases
Ties prefer the later branch because equal `spaceused` is skipped only when current usage is greater or equal. Space values depend on fresh `fs::info()` calls, so concurrent filesystem changes can alter placement between selection and create.

## Test Signals
Exercise branch ordering on ties, ro/nc filtering, min-free-space rejection, stat failure fallback, and search/action parity with `eplus`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lus.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lus.hpp -->
# sources/user-network-fs/mergerfs/src/policy_lus.hpp

## Purpose
Declares the `Policy::LUS` policy family for mergerfs operation routing. The policy name is `lus`, representing the least-used space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lus.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_mfs.cpp

## Purpose
Implements the `mfs` create policy, selecting the eligible branch with the most available space. Existing-path action and search calls use the `epmfs` helpers.

## Important APIs, Types, and Functions
`_create()` scans every `Branch`, obtains `fs::info_t`, checks read-only/no-create and `minfreespace`, and stores the branch with maximum `info.spaceavail`. `Policy::MFS::Action`, `Create`, and `Search` implement the policy interface.

## Control Flow
The create path has a single pass over branches. Each rejected branch updates the candidate error through `error_and_continue`; a valid branch replaces the winner when it has at least as much available space as the current maximum. Action/search delegate to `Policies::Action::epmfs()` and `Policies::Search::epmfs()`.

## State and Persistence Behavior
The implementation is stateless. The selected branch influences later filesystem persistence by choosing where a new object is placed.

## Dependencies and Integration Points
Depends on `fs_info.hpp`, `policy_error.hpp`, and shared policy helpers. It is used by category.create defaults in the Python parity harness.

## Risks and Edge Cases
The later branch wins equal-space ties. Available-space snapshots can become stale before the actual create operation, and low-space branches return `ENOSPC` only if no better branch is found.

## Test Signals
Validate most-free selection, tie behavior, read-only and min-free rejection, and parity of action/search with pre-existing files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_mfs.hpp

## Purpose
Declares the `Policy::MFS` policy family for mergerfs operation routing. The policy name is `mfs`, representing the most-free-space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_msplfs.cpp

## Purpose
Implements `msplfs`: a path-preserving create policy that walks up the requested path and chooses the eligible branch with the least free space among branches where the nearest existing parent path exists.

## Important APIs, Types, and Functions
`_create_1()` searches one `fusepath` level and returns the candidate with minimum `info.spaceavail`. `_create()` repeatedly calls `_create_1()` while replacing the path with its parent until a candidate is found or `/` is reached. Action/search delegate to `eplfs`.

## Control Flow
The create flow preserves locality by first requiring the full path or parent to exist on a branch. Only after no branch matches does it walk to a parent. Eligible branches must be writable, create-capable, not readonly at statvfs time, and above `minfreespace`.

## State and Persistence Behavior
All state is local to branch scanning. Persistence is the eventual caller-created object on the chosen branch.

## Dependencies and Integration Points
Uses `fs_exists`, `fs_info`, `fs_path`, `policy_error`, and `Policies::{Action,Search}::eplfs`. It integrates with path-preserving create policies that prefer existing directory topology.

## Risks and Edge Cases
The code includes `fs_statvfs_cache.hpp` but uses `fs::info()`, so cache expectations should be checked elsewhere. Equal free-space ties prefer later branches, and parent walking can select a less-specific ancestor when the exact path is absent.

## Test Signals
Test exact path hits, parent fallback, root fallback failure, least-free tie behavior, ro/nc/min-free filtering, and action/search consistency with `eplfs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_msplfs.hpp

## Purpose
Declares the `Policy::MSPLFS` policy family for mergerfs operation routing. The policy name is `msplfs`, representing the most-shared-path least-free-space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplus.cpp -->
# sources/user-network-fs/mergerfs/src/policy_msplus.cpp

## Purpose
Implements `msplus`: a most-shared-path create policy that selects the branch with the least used space among eligible branches sharing the target path or nearest existing parent.

## Important APIs, Types, and Functions
`_create_1()` checks one fuse path level and chooses the minimum `info.spaceused`. `_create()` climbs parent paths until a candidate is found. The public policy methods route action/search to `eplus`.

## Control Flow
Create begins at the requested path, filters branches without that path, branches that are read-only/no-create, stat failures, readonly filesystems, and branches below `minfreespace`. If none match, it repeats for the parent path until `/`.

## State and Persistence Behavior
The implementation is stateless and local. The persistent side effect is delegated to the caller that creates an object on the returned branch.

## Dependencies and Integration Points
Depends on `fs_exists`, `fs_info`, `fs_path`, `policy_error`, and common `Policies::Action/Search::eplus` helpers.

## Risks and Edge Cases
Parent fallback may surprise users expecting non-path-preserving least-used behavior. Equal used-space ties keep the earlier candidate because `>=` skips later equal branches. Race windows exist between path existence checks and creation.

## Test Signals
Cover exact and parent path matching, least-used selection, no eligible branch errno propagation, readonly/min-free filters, and equality/tie cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplus.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplus.hpp -->
# sources/user-network-fs/mergerfs/src/policy_msplus.hpp

## Purpose
Declares the `Policy::MSPLUS` policy family for mergerfs operation routing. The policy name is `msplus`, representing the most-shared-path least-used-space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msplus.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mspmfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_mspmfs.cpp

## Purpose
Implements `mspmfs`, a path-preserving variant of most-free-space creation. It picks the branch with the largest available space among branches containing the target path or nearest existing parent.

## Important APIs, Types, and Functions
`_create_1()` scans eligible branches for one path level and returns the maximum `info.spaceavail` candidate. `_create()` performs parent fallback. Public `Action`, `Create`, and `Search` methods bridge to `epmfs` helpers or local create logic.

## Control Flow
The create routine searches the exact path first, then climbs to parents until a branch is found or root is exhausted. Branch filters enforce read/write availability, create permission, stat success, and `minfreespace`.

## State and Persistence Behavior
No state is retained. Branch choice drives the later persistent file or directory placement.

## Dependencies and Integration Points
It depends on branch metadata, `fs::exists()`, `fs::info()`, and `Policies::*::epmfs`, tying it to mergerfs category.create and existing-path operation routing.

## Risks and Edge Cases
Tie handling favors later branches because equal or larger free space replaces the winner. Parent traversal can route new files according to an ancestor directory rather than the requested leaf.

## Test Signals
Validate parent fallback, branch choice by free space, read-only/no-create/min-free rejection, and action/search behavior for existing files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mspmfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mspmfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_mspmfs.hpp

## Purpose
Declares the `Policy::MSPMFS` policy family for mergerfs operation routing. The policy name is `mspmfs`, representing the most-shared-path most-free-space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_mspmfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msppfrd.cpp -->
# sources/user-network-fs/mergerfs/src/policy_msppfrd.cpp

## Purpose
Implements `msppfrd`, combining most-shared-path parent matching with proportional free-space random distribution. Eligible branches are weighted by available space.

## Important APIs, Types, and Functions
`BranchInfo` stores `spaceavail` and a `Branch*`. `_create_1()` collects branch weights for a path level. `_get_branchinfo()` performs parent fallback. `_get_branch()` draws a random threshold with `RND::rand64(sum)` and selects by cumulative weight.

## Control Flow
Create collects candidates from the requested path or nearest existing parent, rejects unavailable branches, sums available space, and randomly chooses a branch with probability proportional to free space. Action/search delegate to `eppfrd`.

## State and Persistence Behavior
The implementation has no persisted state, but it consumes global RNG state through `RND`. The chosen branch determines where later create operations persist data.

## Dependencies and Integration Points
Depends on `fs_exists`, `fs_info`, `policy_error`, `rnd.hpp`, and proportional existing-path helpers in `Policies`.

## Risks and Edge Cases
Random threshold behavior at zero and boundaries must be tested carefully; `RND::rand64(sum)` returns `[0,sum)`, while selection uses `idx < threshold`. Candidate collection is not cleared across parent levels, though it stops at the first non-empty level.

## Test Signals
Use statistical tests for weighted distribution, deterministic mocks if available, parent fallback scenarios, zero-space rejection, and min-free/read-only filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msppfrd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msppfrd.hpp -->
# sources/user-network-fs/mergerfs/src/policy_msppfrd.hpp

## Purpose
Declares the `Policy::MSPPFRD` policy family for mergerfs operation routing. The policy name is `msppfrd`, representing the most-shared-path proportional-free-random-distribution selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_msppfrd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_newest.cpp -->
# sources/user-network-fs/mergerfs/src/policy_newest.cpp

## Purpose
Implements the `newest` policy, selecting the branch whose matching path has the newest modification time. It supports create, action, and search variants with different writeability checks.

## Important APIs, Types, and Functions
`_create()` finds the newest existing path among writable/create-capable branches and checks free space. `_action()` finds the newest writable existing path using `fs::statvfs_cache_readonly()`. `_search()` returns the newest existing path without writeability filtering.

## Control Flow
Each function scans branches, calls `fs::exists()` with `struct stat`, compares `st_mtime`, and stores the best branch. Create also calls `fs::info()` and enforces `minfreespace`; action checks branch and filesystem read-only state; search only requires existence.

## State and Persistence Behavior
No persistent state is kept. The selected newest branch controls which backing object is read, modified, or chosen for a path-preserving create.

## Dependencies and Integration Points
Uses `fs_exists`, `fs_info`, `fs_statvfs_cache`, `policy_error`, and POSIX `stat`. It integrates with policies that need temporal resolution of duplicate files.

## Risks and Edge Cases
Only second-resolution `st_mtime` is considered, so equal mtimes prefer later branches. Newest create requires the path already exists somewhere; missing paths return `ENOENT`. Cached readonly state can differ from fresh statvfs state.

## Test Signals
Test duplicate files with ordered mtimes, equal mtime tie behavior, create low-space errors, action on readonly branches, search on read-only branches, and missing paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_newest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_newest.hpp -->
# sources/user-network-fs/mergerfs/src/policy_newest.hpp

## Purpose
Declares the `Policy::Newest` policy family for mergerfs operation routing. The policy name is `newest`, representing the newest mtime selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_newest.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_pfrd.cpp -->
# sources/user-network-fs/mergerfs/src/policy_pfrd.cpp

## Purpose
Implements `pfrd`, proportional free-space random distribution for create operations across all eligible branches. Action and search use existing-path proportional helpers.

## Important APIs, Types, and Functions
`BranchInfo` records `spaceavail` and `Branch*`. `_get_branchinfo()` filters branches and sums free space. `_get_branch()` draws a random value using `RND::rand64(sum)` and chooses by cumulative weight. `_create()` coordinates these helpers.

## Control Flow
Create scans all branches once, rejecting read-only/no-create, stat failures, readonly filesystems, and branches below `minfreespace`. If the summed available space is nonzero, the branch selection is weighted by each branch's free space.

## State and Persistence Behavior
Only local vectors and the global RNG seed are used. Later create code performs the persistent filesystem mutation.

## Dependencies and Integration Points
Depends on `fs_info`, `policy_error`, `rnd.hpp`, and `Policies::*::eppfrd`. It is intended for balancing writes probabilistically rather than deterministically.

## Risks and Edge Cases
Distribution correctness depends on RNG quality and threshold boundary handling. Very large free-space sums could overflow `u64` if many huge branches are aggregated. Branch state can change between selection and create.

## Test Signals
Run repeated-create distribution checks, zero-sum and all-filtered branch cases, min-free/read-only filtering, and action/search behavior with duplicate paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_pfrd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_pfrd.hpp -->
# sources/user-network-fs/mergerfs/src/policy_pfrd.hpp

## Purpose
Declares the `Policy::PFRD` policy family for mergerfs operation routing. The policy name is `pfrd`, representing the proportional-free-random-distribution selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_pfrd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rand.cpp -->
# sources/user-network-fs/mergerfs/src/policy_rand.cpp

## Purpose
Implements the `rand` policy by delegating to existing eligible-branch policies and shrinking successful results to a single random branch.

## Important APIs, Types, and Functions
`Policy::Rand::{Action,Create,Search}::operator()` call `Policies::Action::all`, `Policies::Create::all`, and `Policies::Search::all`, then use `RND::shrink_to_rand_elem(paths_)` when the helper returns success.

## Control Flow
The policy first gathers all eligible branches for the operation category. If the shared helper fails, it returns that error. If it succeeds and multiple branches were returned, a random element is swapped to the front and the vector is resized to one.

## State and Persistence Behavior
The file is stateless but consumes the process-global RNG seed. Persistence is determined by the caller that acts on the selected branch.

## Dependencies and Integration Points
It depends on `policies.hpp`, `policy_rand.hpp`, and `rnd.hpp`. It composes with the broader policy framework rather than reimplementing branch eligibility.

## Risks and Edge Cases
Random choice is not cryptographic and is modulo-based. Eligibility depends entirely on `all` helpers, so changes there alter `rand` behavior. Multi-branch operations that expected all outputs must not use this policy.

## Test Signals
Test single and multiple eligible branches, helper failure propagation, distribution across repeated runs, and create/action/search category differences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rand.hpp -->
# sources/user-network-fs/mergerfs/src/policy_rand.hpp

## Purpose
Declares the `Policy::Rand` policy family for mergerfs operation routing. The policy name is `rand`, representing the random selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rand.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rv.hpp -->
# sources/user-network-fs/mergerfs/src/policy_rv.hpp

## Purpose
Defines `PolicyRV`, a structured return container for policy operations that need to report both successes and per-branch errors.

## Important APIs, Types, and Functions
`PolicyRV::RV` stores `rv`, `basepath`, and `fullpath`. The parent struct has `std::vector<RV> successes` and `errors`, plus convenience predicates `empty()`, `success()`, and `error()`.

## Control Flow
There is no active control flow beyond predicate evaluation. Callers populate success and error vectors while iterating branches, then inspect aggregate status.

## State and Persistence Behavior
The struct is caller-owned transient state. It does not persist data, but it can describe which underlying branch paths were affected by filesystem operations.

## Dependencies and Integration Points
It depends on `string` and `vector` and is suited for policy or FUSE helpers that need multi-branch result reporting.

## Risks and Edge Cases
`success()` and `error()` are not mutually exclusive; a partial operation can have both successes and errors. Callers must decide precedence and rollback behavior.

## Test Signals
Unit tests should cover empty, success-only, error-only, and mixed states, plus consumers that translate partial results into errno values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_rv.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/predictability.h -->
# sources/user-network-fs/mergerfs/src/predictability.h

## Purpose
Provides branch prediction macros for C/C++ code paths.

## Important APIs, Types, and Functions
Defines `likely(x)` and `unlikely(x)` as `__builtin_expect(!!(x), 1 or 0)`.

## Control Flow
The macros annotate conditions for compiler optimization but do not change program semantics.

## State and Persistence Behavior
No state or persistence is involved.

## Dependencies and Integration Points
Used by performance-sensitive inline helpers such as UID/GID switching paths.

## Risks and Edge Cases
Overuse or incorrect prediction can hurt generated code layout. The macros assume a compiler supporting `__builtin_expect`.

## Test Signals
Compile coverage on supported compilers is sufficient; runtime behavior should match unannotated boolean expressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/predictability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/procfs.cpp -->
# sources/user-network-fs/mergerfs/src/procfs.cpp

## Purpose
Manages cached `/proc` directory handles and exposes thread/process metadata helpers.

## Important APIs, Types, and Functions
`procfs::init()` opens `/proc` and, on Linux, `/proc/self/fd` as `O_PATH` directory fds. `procfs::shutdown()` closes them. `procfs::get_name(tid)` reads `/proc/<tid>/comm` through the cached proc fd.

## Control Flow
Initialization is idempotent and aborts through `fatal::abort()` on required open failures. `get_name()` requires initialization, formats a relative path, opens it with `openat`, reads up to 255 bytes, strips a trailing newline, and returns an empty string on read/open failure.

## State and Persistence Behavior
State is process-global file descriptors `g_PROCFS_DIR_FD` and `procfs::PROC_SELF_FD_FD`. No filesystem content is modified.

## Dependencies and Integration Points
Depends on mergerfs `fs_*` wrappers, `fmt`, scope guards, and Linux procfs. Other low-level code can use `PROC_SELF_FD_FD` for fd-path operations.

## Risks and Edge Cases
The helper is Linux/procfs-specific in practice. `fmt::format_to_n` truncation is not explicitly checked for very large tids. Calling before `init()` aborts the process.

## Test Signals
Test init/shutdown idempotency, current thread name lookup, missing tid behavior, and Linux/non-Linux compilation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/procfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/procfs.hpp -->
# sources/user-network-fs/mergerfs/src/procfs.hpp

## Purpose
Declares the procfs support API used to cache proc directory descriptors and read thread names.

## Important APIs, Types, and Functions
Exports `procfs::PROC_SELF_FD_FD`, `init()`, `shutdown()`, and `get_name(int tid)`.

## Control Flow
The header only declares functions; callers must invoke `init()` before helpers that rely on cached descriptors and `shutdown()` during teardown.

## State and Persistence Behavior
State is the externally defined proc fd. The API does not persist data.

## Dependencies and Integration Points
Includes `<string>` and integrates with low-level fd and thread diagnostics.

## Risks and Edge Cases
Consumers must respect initialization order. `PROC_SELF_FD_FD` is mutable global state and can become invalid after shutdown.

## Test Signals
Compile users against the declarations and run lifecycle tests covering init, read, shutdown, and repeated init.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/procfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/resources.cpp -->
# sources/user-network-fs/mergerfs/src/resources.cpp

## Purpose
Provides process resource setup helpers for mergerfs startup and runtime tuning.

## Important APIs, Types, and Functions
`resources::reset_umask()` clears the umask. `maxout_rlimit()`, `maxout_rlimit_nofile()`, and `maxout_rlimit_fsize()` raise resource limits. `resources::setpriority()` applies a nice value to the process and all current `/proc/self/task` threads.

## Control Flow
Limit raising first tries `RLIM_INFINITY`, then falls back to current hard limit and repeatedly doubles until `setrlimit()` fails. Priority setting calls `setpriority()` for pid 0, scans task ids, parses numeric entries, and sets each thread priority.

## State and Persistence Behavior
Changes are process-global resource and scheduling state. No files are persisted, but `/proc/self/task` is read.

## Dependencies and Integration Points
Uses POSIX resource APIs, procfs task layout, and mergerfs directory wrappers. Startup code can call these helpers before servicing FUSE requests.

## Risks and Edge Cases
The doubling loop can overflow `rlim_t` on unusual platforms. Priority failures are ignored for individual threads. The code assumes `/proc/self/task` exists.

## Test Signals
Test nofile/fsize calls under constrained users, umask reset, priority changes with multiple threads, and behavior when `/proc` is unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/resources.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/resources.hpp -->
# sources/user-network-fs/mergerfs/src/resources.hpp

## Purpose
Declares process resource helper functions.

## Important APIs, Types, and Functions
The `resources` namespace exports `reset_umask()`, `maxout_rlimit(int)`, `maxout_rlimit_nofile()`, `maxout_rlimit_fsize()`, and `setpriority(int)`.

## Control Flow
The header has no runtime flow; callers use the declarations during startup or tuning.

## State and Persistence Behavior
The declared functions mutate process resource state when implemented.

## Dependencies and Integration Points
The header is intentionally small and depends only on function declarations. It integrates with mergerfs initialization code.

## Risks and Edge Cases
Callers must handle negative errno-style returns from implementations.

## Test Signals
Build coverage and startup tests should confirm declarations match implementation and error returns are honored.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/resources.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/rnd.cpp -->
# sources/user-network-fs/mergerfs/src/rnd.cpp

## Purpose
Implements a lightweight process-local pseudo-random generator used by random placement policies.

## Important APIs, Types, and Functions
The constructor-marked `_constructor()` seeds `G_SEED` from `gettimeofday()`. `_rapidhash_rand()` advances the seed and calls `rapid_mix()`. `RND::rand64()` returns raw random values, modulo `[0,max)`, or `[min,max)`.

## Control Flow
The seed is initialized before normal program execution. Each random call mutates `G_SEED`, and bounded calls assert valid ranges before using modulo reduction.

## State and Persistence Behavior
`G_SEED` is a process-global mutable value and is not synchronized. No persistent storage is used.

## Dependencies and Integration Points
Depends on `rapidhash/rapidhash.h`, `base_types`, and random policy code such as `rand`, `pfrd`, and `msppfrd`.

## Risks and Edge Cases
The generator is not cryptographic, is not thread-safe, and bounded values have modulo bias. Assertions disappear in release builds, so callers must avoid zero or invalid bounds.

## Test Signals
Test bounded ranges, seed mutation, repeat-run variability, invalid-bound assertions in debug builds, and concurrent policy stress if used from multiple threads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/rnd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/rnd.hpp -->
# sources/user-network-fs/mergerfs/src/rnd.hpp

## Purpose
Declares the `RND` helper class used for pseudo-random branch selection.

## Important APIs, Types, and Functions
`RND::rand64()`, `rand64(max)`, and `rand64(min,max)` provide random values. The templated `shrink_to_rand_elem(std::vector<T>&)` swaps a random element to index zero and resizes the vector to one.

## Control Flow
The template is a no-op for vectors of size zero or one. For larger vectors it calls `rand64(v_.size())`, swaps, and truncates.

## State and Persistence Behavior
State lives in the implementation's global seed. The template mutates the caller's vector in place.

## Dependencies and Integration Points
Depends on `base_types.h` and `<vector>`. Used by `policy_rand` and weighted placement helpers.

## Risks and Edge Cases
The helper intentionally destroys all but one vector entry. Callers that need the full candidate set must copy first.

## Test Signals
Test empty/single/multi-element vectors, valid range guarantees, and integration with random policies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/rnd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/stat_util.hpp -->
# sources/user-network-fs/mergerfs/src/stat_util.hpp

## Purpose
Provides tiny predicates around POSIX `struct stat`.

## Important APIs, Types, and Functions
`StatUtil::empty()` checks `st_size == 0`; `writable()` checks any user/group/other write bit; `writable_or_not_empty()` combines writable or non-empty.

## Control Flow
All helpers are inline boolean evaluations.

## State and Persistence Behavior
No state is retained and no filesystem changes occur.

## Dependencies and Integration Points
Includes `<sys/stat.h>` and can be used by filesystem operation filters, symlinkification, or cleanup code.

## Risks and Edge Cases
Permission-bit checks do not account for ACLs, capabilities, mount flags, or effective user identity.

## Test Signals
Unit tests should cover regular files, directories, zero-size files, write-bit combinations, and ACL/mount behavior at integration level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/stat_util.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/state.cpp -->
# sources/user-network-fs/mergerfs/src/state.cpp

## Purpose
Defines the global `State state` object and implements dynamic get/set/validation hooks for runtime state exposed through xattrs or control interfaces.

## Important APIs, Types, and Functions
`State::State()` currently performs no registration. `set_getset()` installs a named `GetSet` handler. `get()`, `set()`, and `valid()` look up handlers and return `-ENOATTR` when the key or requested callback is unavailable.

## Control Flow
Lookup uses the `_getset` map. Successful get invokes the stored getter into an output string; set and valid call their stored callbacks with the provided string view.

## State and Persistence Behavior
The global `state` object persists for process lifetime. `_getset` stores callbacks, and `open_files` state is declared in the header. No on-disk persistence is performed.

## Dependencies and Integration Points
Depends on `state.hpp` and `errno.hpp`. It integrates with control xattr code that maps `user.mergerfs.*` keys to live configuration values.

## Risks and Edge Cases
The `_getset` map has no visible synchronization here; concurrent registration and access would need external ordering. Commented-out getattr registration indicates unfinished or removed runtime control surface.

## Test Signals
Test registered get/set/valid callbacks, missing keys returning `ENOATTR`, callback error propagation, and concurrent access expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/state.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/state.hpp -->
# sources/user-network-fs/mergerfs/src/state.hpp

## Purpose
Declares the central process state object for open-file tracking and runtime get/set control handlers.

## Important APIs, Types, and Functions
`State::OpenFile` records `ref_count`, `backing_id`, and `FileInfo*` in a `boost::concurrent_flat_map`. `get_fi()` resolves a `FileInfo` from a FUSE file handle or by nodeid lookup. `GetSet` stores getter, setter, and validator callbacks.

## Control Flow
`get_fi()` first tries `FileInfo::from_fh(fh_)`; if absent it visits `open_files` for `ctx_->nodeid` and returns the stored pointer. The `OpenFile` move constructor uses relaxed atomic loading because insertion is not yet observable.

## State and Persistence Behavior
`open_files` is process-live state for open backing files. `_getset` stores runtime control callbacks. No persistent storage exists beyond backing files handled elsewhere.

## Dependencies and Integration Points
Includes Boost concurrent containers, FUSE request context, `fileinfo.hpp`, and callback machinery. FUSE operations use this to route fd-based operations after unlink or when file handles are encoded differently.

## Risks and Edge Cases
Fallback by nodeid can return a `FileInfo` when `fh` is not directly decodable, so nodeid lifecycle correctness is critical. Callback map access is not shown as concurrent-safe.

## Test Signals
Open-after-unlink tests, concurrent open/release tests, get/set xattr tests, and nodeid/fh fallback coverage are key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/state.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/statvfs_util.hpp -->
# sources/user-network-fs/mergerfs/src/statvfs_util.hpp

## Purpose
Provides inline calculations for `struct statvfs` fields.

## Important APIs, Types, and Functions
`StatVFS::readonly()` checks `ST_RDONLY`; `spaceavail()` returns `f_frsize * f_bavail`; `spaceused()` returns `f_frsize * (f_blocks - f_bavail)`.

## Control Flow
All helpers are single-expression calculations.

## State and Persistence Behavior
No state is retained. They summarize caller-provided statvfs snapshots.

## Dependencies and Integration Points
Used by filesystem info and policy code to normalize free/used/readonly values.

## Risks and Edge Cases
Multiplication can overflow signed `s64` on very large filesystems. `f_bavail` reflects unprivileged availability, not necessarily root-reserved capacity.

## Test Signals
Test readonly flags, expected byte calculations, large values, and consistency with `fs::info()` consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/statvfs_util.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/str.cpp -->
# sources/user-network-fs/mergerfs/src/str.cpp

## Purpose
Implements string utility routines used across config parsing, option formatting, path lists, and glob/prefix matching.

## Important APIs, Types, and Functions
Functions include `split`, `split_to_set`, `split_on_null`, `lsplit1`, `rsplit1`, `splitkv`, `join`, `startswith`, `endswith`, `contains`, `replace_all`, `trim*`, `tolower`, `erase`, `nullterminate`, `matches`, and path/list helpers declared in `str.hpp`.

## Control Flow
Most helpers scan `std::string_view` with find/rfind loops, build vectors or sets, and preserve empty fields where appropriate. Matching helpers use standard string comparisons or `fnmatch()`. Mutation helpers edit caller-provided strings in place.

## State and Persistence Behavior
All state is local or caller-owned. No persistent storage is used.

## Dependencies and Integration Points
Depends on STL containers, algorithms, `<fnmatch.h>`, and `str.hpp`. It is a foundational dependency for config, branches, xattr parsing, and policy option handling.

## Risks and Edge Cases
Delimiter handling intentionally returns empty pieces for repeated/trailing delimiters in some functions; callers must know that behavior. Case conversion with `std::tolower` needs unsigned-char care. `fnmatch` semantics differ from simple substring matching.

## Test Signals
Unit tests should cover empty strings, leading/trailing delimiters, null-delimited data, glob patterns, replacement recursion, trim whitespace, and non-ASCII bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/str.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/str.hpp -->
# sources/user-network-fs/mergerfs/src/str.hpp

## Purpose
Declares shared string utility functions for splitting, joining, matching, trimming, case conversion, and byte/list formatting.

## Important APIs, Types, and Functions
The `str` namespace exports vector/set splitters, `splitkv`, joins for vectors and sets, `startswith`, `endswith`, `contains`, `replace_all`, trim helpers, `tolower`, `erase`, null termination, and match helpers.

## Control Flow
The header provides declarations only; callers link to `str.cpp` implementations.

## State and Persistence Behavior
The declared routines are stateless except for in-place mutation of caller strings where requested.

## Dependencies and Integration Points
Includes STL string, view, vector, set, and utility headers. Many config and path modules depend on this API.

## Risks and Edge Cases
Consumers must understand which helpers return empty tokens and which mutate inputs. API changes here have broad compile-time impact.

## Test Signals
Compile and unit coverage should include all declarations and edge string cases mirrored from `str.cpp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/str.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/strvec.hpp -->
# sources/user-network-fs/mergerfs/src/strvec.hpp

## Purpose
Defines the common `StrVec` alias.

## Important APIs, Types, and Functions
`typedef std::vector<std::string> StrVec;` standardizes string-vector usage in older code.

## Control Flow
No runtime control flow exists.

## State and Persistence Behavior
No state is stored by the header itself.

## Dependencies and Integration Points
Used by config, policy, and parser code expecting `StrVec`.

## Risks and Edge Cases
As a typedef, it cannot be forward declared as a distinct type and offers no semantic constraints.

## Test Signals
Build coverage is sufficient; behavior is inherited from `std::vector<std::string>`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/strvec.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/supported_getdents64.hpp -->
# sources/user-network-fs/mergerfs/src/supported_getdents64.hpp

## Purpose
Detects build-time support for the Linux `getdents64` syscall.

## Important APIs, Types, and Functions
Defines `MERGERFS_SUPPORTED_GETDENTS64` when compiling on Linux and `SYS_getdents64` is available from `<sys/syscall.h>`.

## Control Flow
Preprocessor-only feature detection.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
Used by directory reading implementations to select `getdents64` code paths.

## Risks and Edge Cases
Availability of the syscall macro does not guarantee runtime behavior on every kernel or libc environment.

## Test Signals
Compile matrix tests on Linux and non-Linux targets should verify the macro is or is not defined as expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/supported_getdents64.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/supported_statx.hpp -->
# sources/user-network-fs/mergerfs/src/supported_statx.hpp

## Purpose
Detects build-time support for Linux `statx`.

## Important APIs, Types, and Functions
Defines `_GNU_SOURCE`, includes stat headers, and defines `MERGERFS_SUPPORTED_STATX` when `STATX_TYPE` is available.

## Control Flow
All behavior is controlled by preprocessor checks.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Used by FUSE getattr/statx code to conditionally compile statx support.

## Risks and Edge Cases
Header-level `_GNU_SOURCE` can affect included libc declarations. Macro availability is compile-time only and does not prove syscall success.

## Test Signals
Compile on glibc/musl and non-Linux environments, plus runtime statx parity tests where enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/supported_statx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/symlinkify.hpp -->
# sources/user-network-fs/mergerfs/src/symlinkify.hpp

## Purpose
Implements helper logic for representing old, immutable regular files as symlinks in stat results.

## Important APIs, Types, and Functions
`can_be_symlink()` overloads inspect `struct stat` or `fuse_statx`; `convert()` overloads rewrite mode, size, and block count; `convert_if_can_be_symlink()` applies conversion when timeout and metadata conditions permit.

## Control Flow
A file cannot be symlinkified if it is a directory or has any write bit. The helper compares current time against mtime and ctime using the configured timeout. Conversion changes type to `S_IFLNK`, permissions to `0777`, size to target length, and blocks to zero.

## State and Persistence Behavior
No on-disk file is changed; only caller-provided stat buffers are mutated.

## Dependencies and Integration Points
Depends on FUSE stat types, base integer types, POSIX mode macros, and time. It integrates with getattr/statx presentation paths.

## Risks and Edge Cases
Time comparisons use seconds and can be sensitive to clock changes. Permission-bit checks do not consider ACLs. Mutating metadata can surprise applications expecting backing-file type.

## Test Signals
Test writable, directory, old/new ctime/mtime, negative timeout, stat and statx overloads, and readlink/getattr integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/symlinkify.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/thread_info.hpp -->
# sources/user-network-fs/mergerfs/src/thread_info.hpp

## Purpose
Provides a small helper for estimating current process thread count.

## Important APIs, Types, and Functions
`thread_info::process_count()` calls `fs::lstat("/proc/self/task", &st)` and returns `st.st_nlink - 2`.

## Control Flow
The helper returns a negative errno-style result if `lstat` fails; otherwise it derives count from procfs link count.

## State and Persistence Behavior
No state is retained and no files are modified.

## Dependencies and Integration Points
Depends on `fs_lstat.hpp` and Linux procfs semantics. It can feed diagnostics or resource decisions.

## Risks and Edge Cases
The link-count heuristic is Linux/procfs-specific and may be inaccurate in unusual environments. Return type is `int` while link count is wider.

## Test Signals
Test single-thread and multi-thread counts on Linux, plus failure behavior when procfs is unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/thread_info.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_neg_errno.hpp -->
# sources/user-network-fs/mergerfs/src/to_neg_errno.hpp

## Purpose
Normalizes C/POSIX return values to mergerfs negative-errno style.

## Important APIs, Types, and Functions
Two templated `to_neg_errno()` overloads return `-errno_` when `rv_ == -1`, otherwise the original return value. The one-argument overload captures global `errno`.

## Control Flow
Each helper is a simple conditional expression.

## State and Persistence Behavior
No state is changed. The one-argument form reads `errno`.

## Dependencies and Integration Points
Used by low-level filesystem wrappers to present consistent negative errors to policy and FUSE code.

## Risks and Edge Cases
Callers must call the one-argument overload before any intervening operation changes `errno`. It only treats `-1` as failure, which matches POSIX but not every API.

## Test Signals
Unit tests should cover success values, zero, `-1` with explicit errno, and errno preservation timing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_neg_errno.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_string.cpp -->
# sources/user-network-fs/mergerfs/src/to_string.cpp

## Purpose
Implements numeric `to_string` helpers for fixed-width integer types.

## Important APIs, Types, and Functions
Defines `str::to_string()` overloads for `u64`, `u32`, `u16`, `s64`, `s32`, and `s16`, forwarding to `std::to_string()`.

## Control Flow
Each overload returns immediately from the standard conversion.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Complements `to_string.hpp` and avoids ambiguity around project typedefs from `base_types.h`.

## Risks and Edge Cases
Formatting is base-10 only and locale-independent like `std::to_string` for integers. Missing overloads for other types may select unintended standard overloads.

## Test Signals
Test min/max signed and unsigned values and compile-time overload resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_string.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_string.hpp -->
# sources/user-network-fs/mergerfs/src/to_string.hpp

## Purpose
Declares project-specific numeric string conversion overloads.

## Important APIs, Types, and Functions
The `str` namespace declares `to_string` overloads for `u64`, `u32`, `u16`, `s64`, `s32`, and `s16`.

## Control Flow
Declaration-only header.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Includes `base_types.h` and is used by config/control formatting code.

## Risks and Edge Cases
Overload sets must match definitions in `to_string.cpp` to avoid link failures.

## Test Signals
Compile/link tests for every declared overload and formatting comparisons with expected decimal strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/to_string.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_ref.hpp -->
# sources/user-network-fs/mergerfs/src/tofrom_ref.hpp

## Purpose
Provides a `ToFromString` adapter around a mutable reference and conversion functors.

## Important APIs, Types, and Functions
`TFSRef<T>` stores `T& value`, a `FromFunc`, and a `ToFunc`. `to_string()` calls the to functor; `from_string()` calls the from functor and writes back to `value`.

## Control Flow
Construction captures references and functions. Conversion calls are direct and return the parser's status.

## State and Persistence Behavior
The wrapper mutates the referenced variable but owns no persistent storage.

## Dependencies and Integration Points
Depends on `tofrom_string.hpp`, `string_view`, and functional conversion code used by runtime options.

## Risks and Edge Cases
The referenced object must outlive the wrapper. Parser failures must leave the referenced value in a defined state according to the supplied functor.

## Test Signals
Test successful conversion, parser error propagation, referenced-value mutation, and lifetime assumptions in option registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_ref.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_string.hpp -->
# sources/user-network-fs/mergerfs/src/tofrom_string.hpp

## Purpose
Defines the abstract interface for values that can be read from and written to strings.

## Important APIs, Types, and Functions
`ToFromString` declares pure virtual `to_string()` and `from_string(std::string_view)`. Public flags `display` and `ro` control visibility and read-only behavior in consumers.

## Control Flow
Derived classes implement conversion logic. The base class only defines the contract and default flags.

## State and Persistence Behavior
The base stores two booleans; derived wrappers may reference persistent runtime configuration.

## Dependencies and Integration Points
Used by config and control-file xattr code to expose options uniformly.

## Risks and Edge Cases
No virtual destructor is declared in this file; ownership through base pointers must be audited. Flags are mutable public data.

## Test Signals
Test derived wrappers through the base interface, display/ro handling in control surfaces, and ownership patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_string.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_wrapper.hpp -->
# sources/user-network-fs/mergerfs/src/tofrom_wrapper.hpp

## Purpose
Implements mutable and read-only wrappers that expose ordinary values through the `ToFromString` interface.

## Important APIs, Types, and Functions
`ToFromWrapper<T>` stores `T value`, conversion callbacks, assignment/conversion operators, and `to_string()`/`from_string()`. `ROToFromWrapper<T>` exposes the same read path but rejects writes with `-EROFS` and marks `ro = true`.

## Control Flow
Mutable wrappers parse into `value`; read-only wrappers ignore input and return read-only errors. Operators provide ergonomic access to the contained value.

## State and Persistence Behavior
The contained value is process-live configuration state. No disk persistence is performed by the wrapper.

## Dependencies and Integration Points
Depends on `errno.hpp`, `tofrom_string.hpp`, and project conversion functions. Used for mergerfs runtime options and xattr-backed configuration.

## Risks and Edge Cases
Implicit conversions and assignment operators can hide mutation. Parser functions must validate input fully. Read-only behavior relies on consumers respecting `from_string()` errors and `ro`.

## Test Signals
Test to/from conversions, assignment operators, read-only rejection, display/ro flags, and invalid input behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/tofrom_wrapper.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ugid.cpp -->
# sources/user-network-fs/mergerfs/src/ugid.cpp

## Purpose
Defines thread-local UID/GID tracking variables used by credential switching helpers.

## Important APIs, Types, and Functions
The `ugid` namespace defines thread-local `currentuid`, `currentgid`, and `initialized`.

## Control Flow
There is no active flow in this file; inline functions in `ugid.hpp` read and update these variables.

## State and Persistence Behavior
State is per-thread process memory. It mirrors effective uid/gid after helper-managed changes and is not persisted.

## Dependencies and Integration Points
Includes `<unistd.h>` and backs `ugid::set()` and `ugid::SetGuard`.

## Risks and Edge Cases
Thread-local tracking can become wrong if code changes effective IDs outside `ugid::set()`. Initial values assume root until initialized.

## Test Signals
Test per-thread initialization, repeated set calls, restoration with guards, and interaction with external credential changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ugid.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ugid.hpp -->
# sources/user-network-fs/mergerfs/src/ugid.hpp

## Purpose
Provides helpers for temporarily switching effective UID/GID while serving FUSE requests.

## Important APIs, Types, and Functions
`ugid_t` stores uid/gid from explicit values or `fuse_req_ctx_t`. `ugid::set()` uses raw `setreuid`/`setregid` syscalls and thread-local current IDs. `ugid::SetGuard` switches on construction and restores on destruction.

## Control Flow
`set()` lazily initializes current effective IDs, returns early when already at requested IDs, switches gid then uid, and updates thread-local cache. `SetGuard` asserts current root IDs, calls `set()`, and restores the previous IDs in its destructor.

## State and Persistence Behavior
State is thread-local process credential tracking plus actual effective credentials. No file persistence occurs.

## Dependencies and Integration Points
Depends on FUSE request context, syscall numbers, `predictability.h`, and POSIX credential APIs. Filesystem operations use it to act as the requesting user.

## Risks and Edge Cases
Syscall return values are ignored, so failed credential switches could leave incorrect assumptions. Assertions may be disabled. The guard assumes privileged/root starting state.

## Test Signals
Run privileged tests for set/restore, invalid UID/GID assertions, per-thread isolation, failure handling, and file ownership effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ugid.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/xattr.hpp -->
# sources/user-network-fs/mergerfs/src/xattr.hpp

## Purpose
Centralizes extended attribute feature detection and fallback constants.

## Important APIs, Types, and Functions
When `USE_XATTR` is defined on Linux, it includes `<sys/xattr.h>`. On non-Linux platforms it undefines `USE_XATTR` and emits a pragma message. It defines `XATTR_CREATE` and `XATTR_REPLACE` fallback values if missing.

## Control Flow
All logic is preprocessor-time platform selection.

## State and Persistence Behavior
No runtime state. It controls whether xattr-related code compiles.

## Dependencies and Integration Points
Used by xattr FUSE operations and tests covering `user.mergerfs.*` and POSIX xattrs.

## Risks and Edge Cases
Fallback flag values must match platform ABI expectations. Disabling xattrs at compile time changes user-visible behavior.

## Test Signals
Compile with and without `USE_XATTR`, run xattr mode tests, and verify create/replace flag behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/xattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_api_xattr -->
# sources/user-network-fs/mergerfs/tests/TEST_api_xattr

## Purpose
Validates mergerfs-specific control xattrs such as fullpath, relpath, basepath, and allpaths on a mounted file.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_api_xattr -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_link_rename_exdev -->
# sources/user-network-fs/mergerfs/tests/TEST_cfg_link_rename_exdev

## Purpose
Exercises runtime `link-exdev` and `rename-exdev` fallback modes when branch devices differ.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_link_rename_exdev -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_statfs_ignore -->
# sources/user-network-fs/mergerfs/tests/TEST_cfg_statfs_ignore

## Purpose
Checks runtime `statfs` and `statfs-ignore` options by comparing statvfs capacity fields under different ignore modes.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_statfs_ignore -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_xattr_modes -->
# sources/user-network-fs/mergerfs/tests/TEST_cfg_xattr_modes

## Purpose
Checks runtime xattr modes, especially passthrough success and noattr returning `ENODATA`.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_cfg_xattr_modes -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_create_open -->
# sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_create_open

## Purpose
Verifies read/write behavior on a file created through the mount and reopened through several descriptors.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_create_open -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_open_race -->
# sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_open_race

## Purpose
Stress-tests concurrent open/read/write activity against one mounted file.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_io_passthrough_open_race -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_mount_lifecycle -->
# sources/user-network-fs/mergerfs/tests/TEST_mount_lifecycle

## Purpose
Checks that the shared harness can mount and unmount mergerfs cleanly.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_mount_lifecycle -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_movefile_enospc -->
# sources/user-network-fs/mergerfs/tests/TEST_movefile_enospc

## Purpose
Exercises move-file behavior around ENOSPC or low-space conditions.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_movefile_enospc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_no_fuse_hidden -->
# sources/user-network-fs/mergerfs/tests/TEST_no_fuse_hidden

## Purpose
Ensures mergerfs does not expose or leave unexpected `.fuse_hidden` artifacts in normal directory listings.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_no_fuse_hidden -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_o_direct -->
# sources/user-network-fs/mergerfs/tests/TEST_o_direct

## Purpose
Tests `O_DIRECT` reads with aligned buffers through the mergerfs mount.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_o_direct -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_open_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_open_after_unlink

## Purpose
Checks that an open file descriptor remains usable after its pathname is unlinked.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_open_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_policy_lup -->
# sources/user-network-fs/mergerfs/tests/TEST_policy_lup

## Purpose
Validates least-used-path policy behavior using branch usage and allpaths/fullpath xattrs.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_policy_lup -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_access -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_access

## Purpose
Compares access permission checks through mergerfs and a native directory.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_access -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_bmap -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_bmap

## Purpose
Exercises block mapping ioctl behavior through a mounted file.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_bmap -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_chmod -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_chmod

## Purpose
Compares chmod and mode/stat results for success and error cases.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_chmod -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_chown -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_chown

## Purpose
Compares chown behavior, including self ownership and permission errors.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_chown -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_copy_file_range -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_copy_file_range

## Purpose
Compares `os.copy_file_range()` behavior for small and large sparse copies.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_copy_file_range -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_create_mknod -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_create_mknod

## Purpose
Compares create and mknod behavior for regular files and error paths.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_create_mknod -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_fsync_flush -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_fsync_flush

## Purpose
Compares fsync/flush semantics for files, directories, bad descriptors, and final content.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_fsync_flush -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_getattr_fgetattr -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_getattr_fgetattr

## Purpose
Compares lstat/fstat metadata against native filesystem behavior.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_getattr_fgetattr -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_ioctl -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_ioctl

## Purpose
Compares selected ioctl behavior, especially `FIONREAD`, through mergerfs and native files.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_ioctl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_link_symlink -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_link_symlink

## Purpose
Compares hardlink and symlink creation plus common error paths.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_link_symlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_locking -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_locking

## Purpose
Compares flock and fcntl locking behavior, including contention from a child process.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_locking -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_mkdir_rmdir -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_mkdir_rmdir

## Purpose
Compares mkdir/rmdir success and standard errors.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_mkdir_rmdir -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_open_read_write -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_open_read_write

## Purpose
Compares open/read/write and common open errors.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_open_read_write -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_poll -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_poll

## Purpose
Compares poll readiness masks for mounted and native files.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_poll -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_readdir_plus -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_readdir_plus

## Purpose
Checks listing plus stat behavior over directory entries.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_readdir_plus -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_readdir -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_readdir

## Purpose
Compares directory enumeration, seek/tell behavior, and deleted-entry visibility using libc dirent APIs.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_readdir -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_release -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_release

## Purpose
Checks release/close behavior for open descriptors and file lifecycle.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_release -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_releasedir -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_releasedir

## Purpose
Checks directory close/release behavior using libc directory handles.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_releasedir -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_statfs -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_statfs

## Purpose
Compares statvfs results for mount and native directory expectations.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_statfs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_statx -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_statx

## Purpose
Compares Linux statx metadata and error behavior through mergerfs and native paths.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_statx -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_syncfs -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_syncfs

## Purpose
Tests syncfs syscall behavior on file descriptors from mergerfs.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_syncfs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_tmpfile -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_tmpfile

## Purpose
Tests `O_TMPFILE` support and error behavior.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_tmpfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_truncate_ftruncate -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_truncate_ftruncate

## Purpose
Compares path truncate and fd ftruncate behavior.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_truncate_ftruncate -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_unlink_rename -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_unlink_rename

## Purpose
Compares unlink and rename success/error behavior.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_unlink_rename -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_utimens -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_utimens

## Purpose
Compares utime/utimens behavior for paths, fds, missing paths, and bad descriptors.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_utimens -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_xattr_matrix -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_xattr_matrix

## Purpose
Runs a broader xattr matrix across files, directories, symlinks, and create/replace flags.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_xattr_matrix -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_xattr -->
# sources/user-network-fs/mergerfs/tests/TEST_posix_xattr

## Purpose
Compares basic xattr set/get/list/remove behavior and error cases.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_posix_xattr -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_readlink_semantics -->
# sources/user-network-fs/mergerfs/tests/TEST_readlink_semantics

## Purpose
Compares raw `readlink(2)` return values, errno, and buffer contents for success and error cases.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_readlink_semantics -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_rmdir_enotempty_priority -->
# sources/user-network-fs/mergerfs/tests/TEST_rmdir_enotempty_priority

## Purpose
Ensures rmdir reports `ENOTEMPTY` before less useful branch/path errors when a directory has children.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_rmdir_enotempty_priority -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_unlink_rename -->
# sources/user-network-fs/mergerfs/tests/TEST_unlink_rename

## Purpose
Checks descriptor stability across unlink and rename interactions.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_unlink_rename -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fallocate_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_fallocate_after_unlink

## Purpose
Checks `posix_fallocate()` on an open descriptor before and after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fallocate_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fchmod_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_fchmod_after_unlink

## Purpose
Checks `fchmod()` on an open descriptor before and after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fchmod_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fchown_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_fchown_after_unlink

## Purpose
Checks `fchown()` on an open descriptor before and after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fchown_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fstat_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_fstat_after_unlink

## Purpose
Checks `fstat()` metadata on an open descriptor after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_fstat_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_ftruncate_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_ftruncate_after_unlink

## Purpose
Checks `ftruncate()` on an open descriptor after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_ftruncate_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_futimens_after_unlink -->
# sources/user-network-fs/mergerfs/tests/TEST_use_futimens_after_unlink

## Purpose
Checks fd-based timestamp updates after unlink.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/TEST_use_futimens_after_unlink -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/posix_parity.py -->
# sources/user-network-fs/mergerfs/tests/posix_parity.py

## Purpose
Provides the shared Python harness for mounting mergerfs, creating paired native paths, comparing calls, and manipulating runtime xattr options.

## Important APIs, Types, and Functions
Key helpers include `find_mergerfs()`, `find_fusermount()`, `mount_mergerfs()`, `unmount_mergerfs()`, the `mergerfs_mount()` context manager, `compare_calls()`, `compare_access()`, `touch()`, `cleanup_dir()`, `mergerfs_get_option()`, `mergerfs_set_option()`, `parse_allpaths()`, `mergerfs_branches()`, `underlying_path()`, `pair_paths()`, and `should_compare_inode()`.

## Control Flow
Tests enter `mergerfs_mount()`, which creates temporary branch directories under `tests/.test_tmp`, mounts mergerfs with default `defaults,use_ino,category.create=mfs` options, yields mount and branches, then unmounts and removes the tree. Comparison helpers execute mergerfs and native callables, normalize `OSError.errno`, optionally compare values, and return failure strings.

## State and Persistence Behavior
The harness creates transient test directories and mountpoints and changes live mergerfs options through `user.mergerfs.*` xattrs. It cleans temporary trees on context exit.

## Dependencies and Integration Points
Depends on Python stdlib, `ctypes` access syscall binding, the built or installed `mergerfs` binary, and `fusermount3` or `fusermount`. Every `TEST_*` script imports these helpers.

## Risks and Edge Cases
Missing binaries raise `RuntimeError` and tests convert that to skip code 77. Cleanup can mask unmount failures. Runtime option parsing assumes colon-separated branch entries and xattr control availability.

## Test Signals
The harness itself is exercised by all tests; direct checks should cover missing mergerfs, missing fusermount, mount option overrides, xattr get/set, branch parsing, and cleanup after failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/posix_parity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/run-tests -->
# sources/user-network-fs/mergerfs/tests/run-tests

## Purpose
Discovers and runs every `TEST_*` script with timeout, skip, pass, and fail reporting.

## Important APIs, Types, and Functions
The script scans its own directory with `os.scandir()`, launches each file whose name starts with `TEST_` via `subprocess.Popen`, enforces a 120 second timeout, and treats return code 77 as skip.

## Control Flow
For each test it prints the name, waits for completion, decodes combined stdout/stderr, records failures, kills timed-out children, and exits with status 1 if any test failed.

## State and Persistence Behavior
It does not create persistent state directly, but child tests create temporary mount trees. Output is printed to stdout for CI or local runs.

## Dependencies and Integration Points
Depends on executable `TEST_*` scripts and Python's subprocess module. It is the suite-level entrypoint for the mergerfs Python parity tests.

## Risks and Edge Cases
Directory scan order is filesystem-dependent. A hung cleanup can consume the timeout. Non-executable or non-Python `TEST_*` files would fail at process launch.

## Test Signals
Run with a known passing test, a synthetic skip, a failing script, and a timeout case to validate aggregate exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/run-tests -->
