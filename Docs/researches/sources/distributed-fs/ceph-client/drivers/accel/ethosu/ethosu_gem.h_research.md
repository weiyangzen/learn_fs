# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.h

Purpose: declares Ethos-U GEM private object state, command-stream validation metadata, conversion helper, and BO/command-stream creation APIs.

Important APIs/types: `struct ethosu_validated_cmdstream_info` records copied command size, required size per base-pointer region, and whether each region is written. `struct ethosu_gem_object` embeds `drm_gem_dma_object`, stores optional validation info, and BO flags. `to_ethosu_bo()` converts a DRM GEM object to the private container. Public helpers create generic BOs, BO handles, and command-stream BOs.

Control flow: driver ioctls create BOs through these functions; job submit reads command metadata to validate region handles and set fence dependencies.

State and persistence: metadata persists with the GEM object and is freed by the object free callback.

Dependencies: DRM DMA GEM helper, Ethos-U device definitions, and UAPI flags.

Risks: any object with non-NULL `info` is treated as a command-stream BO and rejected as a region BO. Users of `to_ethosu_bo()` must pass Ethos-U objects only.

Test signals: command BO metadata lifetime, data BO without metadata, handle creation, mmap flag behavior, and region validation in job submit.
