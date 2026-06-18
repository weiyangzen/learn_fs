# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_terratec.c

Purpose: provides the TerraTec PHASE 88 Rack BeBoB spec with custom clock-source detection.

Important APIs/functions: `phase88_rack_clk_src_get` and exported `phase88_rack_spec`; it also defines `phase88_rack_clk_src_types` and a generic rate spec using BeBoB stream get/set functions.

Control flow and state: the clock getter reads two AV/C audio selectors, one for external enable and one for word-clock enable, then maps the combination to internal, S/PDIF external, or word-clock external source IDs. No persistent state is stored in this file.

Dependencies/integration: selected from `bebob.c` ID table and consumed by `snd_bebob_stream_get_clock_src`, proc clock display, and PCM external-clock constraints. Risks include selector function block IDs changing across firmware and ambiguous external/word selector combinations. Test signals are correct proc clock source and rate constraints under internal, S/PDIF, and word-clock modes.
