# File Research: sources/block-storage/linux-dm/drivers/md/raid1-10.c

## Purpose
Provides small shared definitions and helper routines used by RAID1 and RAID10 implementations for resync/recovery bio allocation and special bio markers.

## Main Interfaces
- Resync sizing/constants: `RESYNC_BLOCK_SIZE`, `RESYNC_PAGES`, `NR_RAID_BIOS`.
- Special bio sentinels: `IO_BLOCKED`, `IO_MADE_GOOD`, `BIO_SPECIAL()`.
- Resync page container: `struct resync_pages`.
- Helpers: `rbio_pool_free()`, `resync_alloc_pages()`, `resync_free_pages()`, `resync_get_all_pages()`, `resync_fetch_page()`, `get_resync_pages()`, `md_bio_reset_resync_pages()`.

## Control Flow
`resync_alloc_pages()` allocates the fixed number of pages required for one resync block and unwinds partial allocation on failure. `resync_free_pages()` drops page references, while `resync_get_all_pages()` increments references when multiple bios share the same underlying resync pages. `md_bio_reset_resync_pages()` rebuilds a bio's vector table from the stored pages after `bio_reset()`.

## State And Synchronization
`struct resync_pages` stores the owning raid bio pointer and an array of pages. The helpers do not provide locking; ownership and completion ordering are handled by the including RAID personality.

## Integration Points
Textually included by `raid1.c` here. It is written as shared implementation rather than a separately compiled object, so constants and static helpers become part of the including file.

## Notable Behaviors
- `IO_BLOCKED` and `IO_MADE_GOOD` are encoded as low pointer values and guarded by `BIO_SPECIAL()` before normal bio reference handling.
- User-requested check/repair in RAID1 may allocate distinct page sets per mirror; normal resync can share page references among component bios.

## Risks And Review Focus
- Any code walking `r1bio->bios[]` or equivalent arrays must check `BIO_SPECIAL()` before `bio_put()` or dereferencing.
- `md_bio_reset_resync_pages()` assumes the bio has enough vector capacity for `RESYNC_PAGES`.
- Shared page references require balanced `get_page()` and `put_page()` across all mirrors; mismatches leak or prematurely free resync pages.
