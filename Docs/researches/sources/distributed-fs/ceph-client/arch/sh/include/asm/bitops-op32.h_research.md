# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-op32.h



Source read size: 143 lines, 3915 bytes.



Purpose: SH-2A optimized non-atomic bitops.

Important APIs/types/functions: `arch___set_bit`, `arch___clear_bit`, `arch___change_bit`, test-and variants.

Control flow: constant bit numbers use byte bit instructions; variable cases fall back to word masks.

State and persistence: caller bitmap only.

Dependencies and integration points: generic non-instrumented non-atomic bitops.

Risks and test signals: non-atomic semantics require external locking. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
