# sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.c

## Purpose
Provides shared helper logic for xlator marker xattrs, especially geo-replication marker `xtime` and volume mark aggregation across child subvolumes.

## Important APIs, Types, and Functions
- Default gauges `marker_xtime_default_gauge` and `marker_uuid_default_gauge` define success/failure policies.
- `match_uuid_local()` validates `trusted.glusterfs.<uuid>.xtime` keys.
- `evaluate_marker_results()` maps result counters to errno using gauge policy and `marker_idx_errno_map`.
- `cluster_markerxtime_cbk()` aggregates maximum xtime across children.
- `cluster_markeruuid_cbk()` aggregates/validates volume mark values across children.
- `gf_get_min_stime()` and `gf_get_max_stime()` merge serialized stime values into a dict using network/host time comparison.
- `cluster_handle_marker_getxattr()` validates caller and key, allocates local aggregation state, asks caller-supplied `populate_args()` for subvolumes/gauge overrides, winds getxattr to each selected child, and unwinds with aggregate result.

## Control Flow
`cluster_handle_marker_getxattr()` only handles gsynchronization daemon calls (`GF_CLIENT_PID_GSYNCD`) and marker xattr names. It sets `frame->local` to `xl_marker_local_t`, winds child getxattr requests, and child callbacks decrement `call_count` under `frame->lock`. When the last callback arrives, `cluster_marker_unwind()` restores the caller's previous local state, optionally adds aggregate data to a dict, evaluates counters against the gauge, and uses a specialized unwind callback or default getxattr unwind.

## State and Persistence
Per-aggregation state lives in `xl_marker_local_t`: selected volume UUID, aggregate time buffers or volume mark, result counters, gauge, child call count, and saved caller local. Persistent data being read is marker xattrs on child bricks.

## Dependencies and Integration Points
Depends on dict APIs, GlusterFS stack winding, child xlator lists, marker xattr naming, network byte order helpers, and gsyncd PID conventions. Used by cluster translators that need marker xattr aggregation and supply `populate_args()`.

## Risks
- Uses `alloca(num_subvols * sizeof(*subvols))`; zero or very large child counts deserve scrutiny.
- `cluster_markeruuid_cbk()` allocates/replaces `local->volmark`; failure and cleanup paths must avoid leaks.
- Gauge policy is compact but non-obvious; incorrect custom gauge from `populate_args()` changes error semantics.
- The code assumes callbacks arrive exactly `call_count` times and uses shared `frame->lock`.

## Test Signals
Tests should cover marker key validation, gsyncd-only access, xtime max aggregation, volume mark major/minor mismatch, child ENOENT/ENODATA/ENOTCONN error policies, custom `populate_args()` gauges, and min/max stime dict merges.
