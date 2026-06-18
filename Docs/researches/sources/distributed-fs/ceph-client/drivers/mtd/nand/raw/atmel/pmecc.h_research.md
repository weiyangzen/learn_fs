# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.h

Purpose: public interface between the Atmel NAND controller and PMECC engine implementation. It defines auto-selection constants, the user request shape, opaque PMECC types, and exported function prototypes.

Important APIs/types/functions: `ATMEL_PMECC_MAXIMIZE_ECC_STRENGTH`, `ATMEL_PMECC_SECTOR_SIZE_AUTO`, and `ATMEL_PMECC_OOBOFFSET_AUTO` request automatic choices. `struct atmel_pmecc_user_req` carries page size, OOB size, ECC strength, bytes, sector size, sector count, and OOB offset. Declared functions cover engine acquisition, user creation, reset, enable/disable, ready wait, sector correction, erased-chunk policy, and generated ECC bytes.

Control flow: none in the header. Controllers include it, call `devm_atmel_pmecc_get`, create a user, then call enable/wait/correct/generate/disable around page I/O.

State and persistence: `struct atmel_pmecc` and `struct atmel_pmecc_user` are opaque. The request object is mutable: user creation writes back selected geometry.

Dependencies/integration: included by Atmel NAND/PMECC code and depends on kernel types such as `bool` and `struct device` being available to includers.

Risks/test signals: callers may incorrectly treat request fields as input-only. Compile coverage should catch missing type dependencies; runtime tests should validate auto constants, invalid geometry rejection, and raw NAND page/OOB paths using this API.
