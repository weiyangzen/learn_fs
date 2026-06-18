<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h

Purpose: Defines SN0 hub Network Interface registers and bitfields for link status, routing/vector PIO, age controls, LLP parameters/errors, routing tables, and region-size detection.

Important APIs/types/functions: `NI_*` register offsets, status masks `NSRI_*`, reset/protection masks, global/diagnostic parameter fields, vector PIO fields `NVP_*` and `NVS_*`, age control fields, port parameter/error fields, routing table helpers, `hubni_port_error_t`, LLP maxima, and inline `get_region_shift()`.

Control flow: SN networking/topology code reads NI status to determine node ID, link state, region mode, and hub revision; programs routing/vector PIO and age controls; handles port errors; and uses routing table macros for meta/local routes.

State and persistence: State is NI hardware: link/reset/protection, vector PIO status/data, aging parameters, LLP port parameters/errors, and routing table entries.

Dependencies and integration points: Depends on Linux types for C builds and on `LOCAL_HUB_L` from SN address accessors through includers.

Risks: Reset bits can reset the link or hub. Region shift controls NASID-to-region interpretation and must match hardware status. Wrong routing table or vector PIO programming can isolate nodes.

Test signals: SN multi-node boot, NI link status/routing table validation, vector PIO tests, link error injection, and region-size detection tests are useful.

Source read size: 263 lines, 9525 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h -->
