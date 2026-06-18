# sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.h

Purpose: defines the raw event encoding, constraint bit layout, MMCR bit helpers, SIER decoding masks, and exported helper prototypes shared by PowerISA v2.07 and later PowerPC PMU implementations.

Important APIs/types/functions: event bit macros for EBB/BHRB/IFM/threshold/sample/cache/PMC/unit/combine/marked fields; POWER9 and POWER10 format variants such as `p9_EVENT_VALID_MASK`, `p10_EVENT_VALID_MASK`, `p10_EVENT_MMCR3_MASK`, and `p10_EVENT_THR_CMP_MASK`; constraint macros `CNST_*`, `ISA207_ADD_FIELDS`, `ISA207_TEST_ADDER`; MMCR helpers `MMCR1_*`, `MMCRA_*`, `MMCR2_*`, `MMCR3_SHIFT`; SIER helpers and prototypes for `isa207_*` functions.

Control flow and state: no runtime control flow. The file encodes the contract used by constraint solvers and PMU descriptors to translate perf event config fields into MMCR register values.

State and persistence behavior: no state. Macro constants become ABI-facing sysfs format semantics and internal register programming rules.

Dependencies and integration points: included by `isa207-common.c` and newer processor PMU files. It depends on perf event definitions, PowerPC firmware/cputable headers, `internal.h`, and shared PowerPC PMU types such as `struct mmcr_regs`.

Risks: macro shifts and masks are hardware contracts; any mismatch breaks raw event programming, group scheduling, or sampling. Power10 moved threshold compare into `attr.config1`, so users and callers must handle the extra attribute flag. Constraint adder fields must remain aligned with the generic solver's overflow checks.

Test signals: compile all ISA207-family PMUs; inspect `/sys/bus/event_source/devices/cpu/format/*`; run raw event groups with pinned/unpinned PMCs, threshold fields, BHRB/EBB, Power10 MMCR3 fields, and perf memory sampling.
