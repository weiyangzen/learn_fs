# sources/control-plane/ceph-csi/cmd/cephcsi.go

Purpose: main entrypoint for the `cephcsi` binary; parses CLI flags, validates configuration, writes Ceph config, and dispatches to RBD, CephFS, NFS, NVMe-oF, liveness, or controller mode.

Important APIs/types/functions: `init` registers flags into global `util.Config`; `getDriverName` selects defaults; `printVersion`; `main`; `setPIDLimit`; `initControllers`; `validateCloneDepthFlag`; `validateMaxSnapshotFlag`; `logAndExit`.

Control flow: `main` handles `--version`, initializes feature gates, requires `--type`, validates driver name, optionally runs `automaxprocs`, adjusts PID limits for node servers, validates metrics URL for profiling/liveness, writes Ceph config, then switches on `conf.Vtype` to run the selected driver/controller.

State and persistence behavior: process-global `conf` holds parsed runtime state. `util.WriteCephConfig` writes local Ceph client config. Controllers and drivers create external Kubernetes/Ceph state through their packages.

Dependencies and integration points: imports internal driver packages, controller packages, liveness, util/log, automaxprocs, klog, controller-runtime logging, and kernel version utility.

Risks: no default driver for unknown type; errors exit the process. RBD clone/snapshot thresholds are hard validated. Deprecated `--setmetadata` is still passed by manifests but logged as no-op. PID-limit changes are best-effort.

Test signals: unit tests likely cover validation helpers elsewhere; deployment/e2e manifests exercise mode selection and flag compatibility.
