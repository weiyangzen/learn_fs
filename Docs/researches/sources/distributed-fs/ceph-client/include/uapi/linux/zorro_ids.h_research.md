<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h

Purpose: provides the sorted public manufacturer and product ID database for Amiga Zorro expansion boards.

Important APIs and types: `ZORRO_MANUF_*` constants assign manufacturer IDs, while `ZORRO_PROD_*` constants compose full IDs through `ZORRO_ID(manuf, prod, epc)`. The list covers Commodore, GVP, Phase5, Village Tronic, Individual Computers, MacroSystem, and many other official, unofficial, and test IDs, including documented ID clashes.

Control flow, state, and persistence: no control flow or state; bus drivers and module tables use these constants to match enumerated AutoConfig boards.

Dependencies and integration points: included by `zorro.h`, kernel Zorro drivers, module alias generation, and userspace tooling that decodes board IDs.

Risks and test signals: risks include unsorted additions, duplicate/clashing IDs, misspelled macro names becoming ABI, and dependency on `ZORRO_ID` being defined by the includer. Test compile inclusion through `zorro.h`, driver ID tables, known-board matching, and duplicate-ID review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h -->
