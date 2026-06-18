# sources/distributed-fs/ceph/src/mds/balancers/greedyspill.lua

Purpose: Implements a simple Lua MDS balancer policy that spills half of the local metadata load to the next rank when this rank is loaded and the neighbor is idle.

Important APIs/functions: Local functions `mds_load`, `when`, and `where` operate on the balancer-provided globals `mds`, `whoami`, and `BAL_LOG`. The returned `targets` table maps ranks to desired exported load amounts.

Control flow: The script initializes every rank target to zero, computes `mds[rank].load` from `all.meta_load`, logs selected metrics, checks whether `mds[whoami+1]` exists, and if local load is above `0.01` while the next rank is below `0.01`, assigns half the local load to the neighbor.

State and persistence behavior: No persistent state. It mutates the in-memory `mds` table by assigning `load` and returns a target map to the balancer framework.

Dependencies and integration points: Depends on the MDS balancer Lua environment exposing rank metrics and logging. Uses metrics `auth.meta_load`, `all.meta_load`, `req_rate`, `queue_len`, and `cpu_load_avg`.

Risks: The comment says Lua tables are 1-indexed, but the code also treats rank adjacency as `whoami+1`; correctness depends on how Ceph passes rank keys. It only considers the next rank and only spills from nonzero to near-zero load, so it can leave imbalance among active ranks untouched.

Test signals: Run with synthetic `mds` maps for last-rank, loaded/idle neighbor, loaded/loaded neighbor, and missing metrics. Verify returned target keys match balancer rank indexing.
