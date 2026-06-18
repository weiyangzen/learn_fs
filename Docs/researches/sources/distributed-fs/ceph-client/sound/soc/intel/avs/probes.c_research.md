# sources/distributed-fs/ceph-client/sound/soc/intel/avs/probes.c

Purpose: Registers a compressed capture component for AVS probe extraction and manages the firmware probe module plus host HDA stream used to copy extracted samples to userspace.

Important APIs/functions: `avs_register_probe_component()` registers the component and DAI. Compressed callbacks include open/free/set_params/trigger/pointer/copy. Internal helpers initialize/delete the firmware probe module and fetch the assigned host stream.

Control flow: Open enforces a single extractor stream and assigns an HDA host stream. Set params allocates compressed pages, programs HDA format/setup, disables D0ix for active probing, initializes the probe module on first stream, and increments `num_probe_streams`. Trigger starts/stops the HDA stream under `bus->reg_lock`. Free disconnects probe points targeting the extractor node, deletes the probe module when the last stream closes, reenables D0ix, cleans up stream/pages, and clears `adev->extractor`.

State and persistence: Uses `adev->extractor` as singleton host stream, `adev->num_probe_streams` as lifetime count, stream private data, and firmware probe module instance zero.

Dependencies and integration: Depends on compressed ALSA APIs, HDA stream helpers, AVS debug/probe IPCs, module metadata lookup, D0ix control, and firmware probe UUID definitions.

Risks: Error paths in `set_params()` after page allocation or stream setup rely on later shutdown for cleanup. Copy returns `count - ret` on copy fault, which follows partial-copy semantics but deserves testing. Probe-point disconnection filters by vindex only. Singleton extraction prevents concurrent users.

Test signals: Compressed open/set_params/trigger/copy/free, concurrent open rejection, D0ix disable/enable balance, probe point connect/disconnect through debug tooling, and wraparound copy from ring buffer.
