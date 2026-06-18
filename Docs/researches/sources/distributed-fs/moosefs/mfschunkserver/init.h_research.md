# sources/distributed-fs/moosefs/mfschunkserver/init.h

## Purpose
`init.h` defines the chunkserver module startup order through table-driven arrays consumed by the common MooseFS daemon launcher.

## Important APIs and control flow
The local `runfn` type is `int (*)(void)`. `RunTab` calls `rnd_init`, `hdd_init`, `mainserv_init`, `job_init`, `csserv_init`, `masterconn_init`, and `chartsdata_init`, ending with a null sentinel. The comment on `csserv_init` says it must run before `masterconn_init`, because master registration needs the chunkserver listener endpoint. `LateRunTab` starts `hdd_late_init`; `RestoreRunTab` calls `hdd_restore`.

## Integration, persistence, and risks
This file sequences storage, networking, jobs, master connection, and charts. Persistence is delegated to the HDD functions, but the ordering ensures restore and storage-thread startup happen in the intended phases.

The main risk is order regression. Tests should verify module order, init failure propagation, restore-mode execution, and late-init execution after normal init.
