# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.c

Purpose: full Intel Processor Trace packet stream decoder. It turns raw PT packets and caller-provided instruction walking into `intel_pt_state` samples: branches, instruction samples, transaction events, PTWRITE, power/events, PSB events, block items, cycle/timestamp data, trace begin/end, and decode errors.

Important APIs and types: public functions are `intel_pt_decoder_new()`, `intel_pt_decoder_free()`, `intel_pt_decode()`, `intel_pt_fast_forward()`, `intel_pt_find_overlap()`, `intel_pt__strerror()`, and `intel_pt_set_first_timestamp()`. Internally `struct intel_pt_decoder` stores callbacks, current buffer, compressed IP state, TNT packet state, return-compression stack, packet context, PSB sync state, timing conversion state, CBR/CYC/MTC/TMA data, VMCS/TSC correlation data, pending FUP-attached event flags, block item state, and loop protection counters.

Control flow: construction copies callback parameters and timing configuration. `intel_pt_decode()` dispatches on `pkt_state`: synchronize to PSB, synchronize to IP after errors, walk normal trace, continue TNT/TIP/FUP handling, resample, or run VM time correlation. Packet walking uses `intel_pt_get_next_packet()` and the packet decoder. TNT drives conditional branch decisions; TIP handles indirect branches and trace enable/disable; FUP attaches asynchronous events and may be followed by TIP; PSB/PSBEND resynchronize and collect side-band timing/mode data. Instruction walking is delegated to `params->walk_insn`, while `get_trace` supplies buffers and `lookahead` supports fast-forward.

State and persistence: all decode progress is in-memory. It mutates decoder state heavily across calls, including IP, last-IP compression, return stack, transaction flags, timestamps, cycle counts, and pending event payloads. VM time correlation can rewrite mmap-backed trace bytes for translated guest TSC unless dry-run is set.

Dependencies and integration: depends on auxtrace alignment constants, PT packet decoder, x86 instruction decoder, PT log, and consumer callbacks supplied by higher perf auxtrace code.

Risks: high state-machine complexity, many recovery paths, packet split handling, timestamp wrap/slip heuristics, VM TSC offset guessing, infinite-loop protection, and unsupported/malformed packet cases. Callback correctness is critical; bad instruction walking produces mismatches or resync.

Test signals: packet-stream fixtures for TNT/TIP/FUP/PSB/OVF/PTWRITE/power/block events, timestamp conversion cases, VM correlation dry-run and rewrite cases, overlap detection with and without TSC, fast-forward positioning, error-code mapping, and loop-limit behavior.
