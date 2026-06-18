## sources/distributed-fs/ceph-client/fs/isofs/rock.h

Purpose: defines packed SUSP and Rock Ridge record structures and flag constants used by `rock.c`.

Important types: includes `SU_SP_s`, `SU_CE_s`, `SU_ER_s`, RR records for PX, PN, SL, NM, CL, PL, TF, and Linux-specific ZF, plus the top-level `struct rock_ridge` signature/length/version union. `struct SL_component` uses a counted flexible array for symlink components.

Control flow and state: no executable logic. The layouts directly govern how untrusted on-disc system-use bytes are interpreted by the parser. Flag constants define RR capability bits and TF timestamp fields.

Dependencies and integration points: depends on ISO/SUSP/RRIP on-disk formats and is included only by Rock Ridge parsing code.

Risks and test signals: structure packing and minimum-size assumptions are critical. Any layout drift can break parsing or bounds checks. Test with compiler layout validation indirectly through mounting known Rock Ridge images and fuzzing malformed records.
