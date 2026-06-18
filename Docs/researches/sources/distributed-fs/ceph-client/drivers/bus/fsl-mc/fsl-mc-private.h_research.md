# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-private.h

Purpose: central private contract for the FSL MC bus implementation. It defines MC firmware command IDs, packed command/response structures, minimum supported object API versions, DPRC/DPBP/DPCON/generic object command interfaces, resource-pool bookkeeping, UAPI state, and internal helper prototypes shared by bus, IRQ, allocator, DPRC, portal, and UAPI code.

Important types and APIs: command structs include DPMNG version response, DPMCP open/close/reset, DPRC IRQ/config/object/region/connection messages, DPBP/DPCON attributes, and generic object open/reset. `struct fsl_mc_resource_pool` owns typed free lists with a mutex. `struct fsl_mc_uapi` tracks the miscdevice and shared static portal use. `struct fsl_mc_bus` embeds the DPRC `fsl_mc_device`, resource pools, IRQ resources, scan mutex, DPRC attributes, UAPI object, and IRQ enabled state.

Control flow role: this header is not executable but defines the ABI used by command builders in `mc-sys.c`, DPRC code, `obj-api.c`, and `fsl-mc-bus.c`. The command IDs encode firmware API versions and command numbers; consumers fill command structures, call `mc_send_command()`, then decode little-endian responses.

State and persistence: declares in-memory resource pools, UAPI portal-use state, and per-bus scan/IRQ state. It does not persist data across boots; MC firmware is the authoritative source for object/container attributes.

Dependencies and integration: depends on public `<linux/fsl/mc.h>`, mutex/list/device model, miscdevice/ioctl support, and all FSL MC subsystem compilation units. Its fallback inline UAPI functions make `CONFIG_FSL_MC_UAPI_SUPPORT` optional without changing bus probe behavior.

Risks: command layout must match firmware exactly, including endian and padding; version constants gate portal/object support; structs shared between files can create subtle ABI drift if changed without command encoders/decoders. Test signals include building with and without UAPI, DPRC object scan, IRQ allocation, resource pool allocation/free, generic object open/close/reset, and compatibility against supported MC firmware versions.
