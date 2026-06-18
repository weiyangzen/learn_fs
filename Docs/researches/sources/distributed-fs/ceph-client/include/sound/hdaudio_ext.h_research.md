# sources/distributed-fs/ceph-client/include/sound/hdaudio_ext.h

Source read summary: 149 lines, extended HD-audio bus/link/stream contracts for ASoC and multi-link platforms.

Purpose: extends generic HDA core with link objects, extended streams, DMA parameter helpers, and bus operations used by Intel SST/SOF/ASoC HDA-style controllers.

Important APIs, types, and functions: `struct hdac_ext_link` tracks per-link index, capability address, codec mask, ML address, refcount, lock, and list nodes. `struct hdac_ext_stream` wraps `hdac_stream` with decoupled host/link DMA state, link stream tag/index/substream, and list nodes. APIs initialize/free extended bus and streams, assign/release streams, set up/clear host and link DMA, start/stop streams, sync start/stop, set stream IDs, enable links, get/set link power, configure stream decoupling, and open/close streams.

Control flow: extended controller probe initializes link lists, enumerates links from capability registers, allocates extended stream objects, then ASoC/SOF paths assign host/link streams separately and power links on demand before programming DMA.

State and persistence behavior: state is runtime kernel/controller state: link refcounts and power flags, assigned stream tags, decoupled host/link DMA flags, and stream lists. No disk persistence is involved.

Dependencies and integration points: includes HDA core and register definitions. It integrates with ASoC Intel DSP drivers, HDA multi-link controllers, SoundWire-adjacent HDA link management, and DMA parameter setup.

Risks and edge cases: host/link decoupling can leak stream tags or leave link DMA running; refcounted link power must balance under concurrent DAIs; capability parsing must handle missing or alternate ML registers.

Test signals: extended stream allocation, host/link setup and teardown, stream reset with decoupled mode, link power refcounting, multi-link enumeration, and SOF/SST playback/capture suspend/resume.
