## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPage.h

**Purpose:** Defines a small wrapper around a kernel `struct page` with mapped data and used length for BeeGFS page-vector IO.

**Important APIs/types/functions:** Defines `struct FhgfsPage` and inline helpers `FhgfsPage_unmapUnlockReleasePage`, `FhgfsPage_unmapUnlockReleaseFhgfsPage`, `getFileOffset`, `zeroPage`, and `getPageIndex`.

**Control flow:** Page-list code maps pages with `kmap`; cleanup helpers `kunmap`, unlock, and `put_page`. Offset/index helpers read kernel page metadata. `zeroPage` clears the entire mapped page data.

**State and persistence behavior:** Holds a borrowed/referenced page pointer, mapping address, and used byte count. Page contents are real filesystem data; helper state is transient.

**Dependencies and integration points:** Used by `FhgfsPageListVec`, `FhgfsChunkPageVec`, remoting page IO, and buffered read/write completion paths.

**Risks:** Cleanup assumes the page was kmapped and locked and has a held reference. Calling cleanup twice or on an unmapped page would corrupt page state. `zeroPage` clears the full page, so callers must ensure that is intended for partial-page handling.

**Test signals:** Validate map/unmap/unlock/refcount lifecycle, page offset/index values, zeroing behavior for partial pages, and error cleanup idempotence expectations in callers.
