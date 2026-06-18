# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_in_user.S

Purpose: Raw copy between two user-space addresses on SPARC64.

Important APIs/functions: Exports `raw_copy_in_user`.

Control flow: Uses ASI-based loads and stores for both source and destination, protected by exception table entries. It chooses aligned xword, 32-bit, and byte-copy paths similar to generic memcpy and returns remaining bytes on fault.

State and persistence: No persistent state; mutates user destination and uses `%asi`.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, and `asm/asi.h`; used as fallback by copy-to/from-user wrappers when the current ASI is not the expected one.

Risks/test signals: Dual user-source/user-destination faults and residual counts are key. Test source fault, destination fault, overlap expectations, and all alignment/length paths.
