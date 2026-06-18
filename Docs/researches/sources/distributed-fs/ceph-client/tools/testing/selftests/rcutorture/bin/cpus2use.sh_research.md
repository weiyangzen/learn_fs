# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/cpus2use.sh

Purpose: estimates how many host CPUs rcutorture should use when no explicit count is available.

Important APIs and functions: honors `TORTURE_ALLOTED_CPUS`, otherwise counts processors in `/proc/cpuinfo`, optionally estimates idle CPUs via `mpstat`, and uses awk to choose at least one and at least 10 percent of CPUs.

Control flow: return configured allotment if present; compute CPU and idle counts; round up final CPU count.

State and persistence: read-only.

Dependencies and integration: fallback for `configNR_CPUS.sh` and scheduling logic.

Risks and test signals: `/proc/cpuinfo` processor count and `mpstat` field positions are platform/tool-version sensitive. Overestimation can overload hosts; underestimation reduces coverage.
