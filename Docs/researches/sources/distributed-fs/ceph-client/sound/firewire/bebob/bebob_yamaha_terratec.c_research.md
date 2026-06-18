# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_yamaha_terratec.c

Purpose: supplies the shared Yamaha GO44/GO46 and TerraTec PHASE 24/X24 BeBoB spec with clock source lookup and generic rate handling.

Important APIs/functions: `clk_src_get` and exported `yamaha_terratec_spec`; it defines clock source types for internal and S/PDIF external sources.

Control flow and state: the clock getter reads AV/C selector function block 4, validates the returned index, and maps it to a clock type. Rate get/set use the generic BeBoB stream helpers. The file stores no runtime state.

Dependencies/integration: selected from the BeBoB ID table and used by clock/rate/proc/PCM paths. The comments document device behavior at 192 kHz and interactions with mixer transactions. Risks include noisy high-rate operation if asynchronous mixer traffic continues, selector ID assumptions, and unsupported clock IDs. Test signals are valid clock reporting, successful high-rate streaming with mixer traffic minimized, and rate constraints matching discovered formations.
