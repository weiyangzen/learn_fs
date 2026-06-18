# sources/distributed-fs/lizardfs/src/master/init.h

Purpose: defines master initialization run tables and version identifier for the LizardFS master process.

Important APIs/types/functions: `RunTab` lists startup functions and display names; `EarlyRunTab` validates personality before main initialization; `LateRunTab` is empty. The run order starts with `hstorage_init`, then personality, random generator, data cache, sessions, exports, topology, filesystem, charts, master/metalogger/chunkserver/taperserver/client networking.

Control flow: the master main framework iterates these tables to initialize subsystems. Comments document ordering constraints, especially name storage first, personality second, data cache/sessions before filesystem, and client network after filesystem.

State and persistence behavior: no persistent state here, but startup order determines when metadata/session/export state is loaded and when name storage handles are safe.

Dependencies/integration: includes subsystem headers for every initialization function and exposes the `id` version string.

Risks and test signals: order is critical and mostly encoded by comments plus table position. Tests or startup checks should catch accidental reordering of `hstorage_init`, personality validation/init, session load, and filesystem init.
