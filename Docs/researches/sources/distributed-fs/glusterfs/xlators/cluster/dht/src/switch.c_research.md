# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/switch.c

## Purpose
Implements the switch DHT variant, which routes files matching configured path patterns to selected child subvolumes while retaining DHT hashing, linkfiles, layouts, and common FOPs. It is a pattern-aware placement/lookup scheduler layered over DHT.

## Important APIs and Types
- `struct switch_struct`: linked-list pattern rule containing a glob pattern, eligible child array, round-robin node index, and child count.
- `set_switch_pattern`: parses `pattern.switch.case` strings like `*.jpg:child1,child2;*.mpg:child3`, validates child names, builds rule list, and adds a default `*` rule for unmentioned children.
- `get_switch_matching_subvol`: returns the hashed subvolume if it is eligible for a matching rule; otherwise picks the next eligible child round-robin.
- `switch_lookup` / `switch_local_lookup_cbk`: route fresh lookup through the pattern-selected child, then handle regular files, directories, linkfiles, and fallback search.
- `switch_create` and `switch_mknod`: place new objects on pattern-selected/free subvolumes and create linkfiles when placement differs from hash.
- `switch_fini` / `switch_init`: manage pattern rule memory around shared DHT lifecycle.

## Control Flow
Initialization calls `dht_init` then parses `pattern.switch.case`. Rule parsing builds a temporary all-child array, marks children already assigned by explicit patterns, rejects unknown child names and overlong patterns, and finally appends a default `*` rule for remaining children. Lookup revalidation follows existing layout. Fresh lookup asks for layout and linkto xattrs, computes the hash, selects a switch subvolume by `fnmatch`, and either uses normal DHT lookup on the hashed child or switch-local lookup on the selected child. Directory and linkfile handling then converge with DHT callbacks.

Create/mknod compute the hashed child, choose the matching rule child, fall back to free-space selection if filled, and either create directly on the hashed child or create a linkfile on hash then create the real object on the selected child.

## State and Persistence
`conf->private` stores the head of the switch rule linked list. Each rule mutates `node_index` for round-robin scheduling. Persistent effects are backend file creation and DHT linkto xattrs when selected placement differs from hashed placement.

## Dependencies and Integration Points
Uses `fnmatch`, DHT shared init/fini/options, DHT lookup callbacks, linkfile creation, disk-usage selection, child xlator names, and common DHT FOPs for all non-placement operations. `xlator_api` identifies the translator as `"switch"` and tech preview.

## Risks
- `node_index` is incremented without locking, so concurrent creates/lookups can race and skew round-robin selection.
- `set_switch_pattern` frees only part of the temporary state on some error paths; ownership is intricate.
- The parser ignores explicit `*` rules and creates its own default, which can surprise administrators.
- Pattern strings longer than 255 bytes are rejected, but rule syntax has limited validation around missing `:` pieces.
- Like NUFA, non-hashed placement depends on linkfiles and later self-heal/rebalance to keep namespace consistent.

## Test Signals
No direct switch tests are in this subset. High-value tests should cover parser success/failure, unknown child rejection, default `*` construction, round-robin among eligible children, hashed-child eligibility short-circuit, full-subvolume fallback, linkfile creation, and concurrent rule selection.
