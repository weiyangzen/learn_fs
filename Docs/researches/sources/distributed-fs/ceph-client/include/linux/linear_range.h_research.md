# sources/distributed-fs/ceph-client/include/linux/linear_range.h

Purpose: declares helpers for converting between linear hardware selectors and physical values such as voltages or currents.

Important APIs and types: `struct linear_range` stores minimum value, minimum selector, maximum selector, and step. `LINEAR_RANGE` and `LINEAR_RANGE_IDX` initialize tables. Helper APIs count values, compute max, map selector to value, map arrays of ranges, select low/high fitting selectors with found flags, and clamp a selector within a range.

Control flow: regulator/PMIC drivers define selector tables and call lookup helpers when translating user/framework values to register selectors or reading register values back.

State and persistence: no state is owned; functions operate on caller-provided static tables.

Dependencies and integration points: depends on basic types and integrates with regulator, power, LED, and analog-control drivers that use linear register encodings.

Risks and test signals: risks include off-by-one selector bounds, zero step handling, array ordering assumptions, and low/high rounding semantics. Test selectors at min/max, below/above range values, multi-range gaps/overlaps, exact matches, and clamped selection.
