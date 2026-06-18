# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.h

## Scope

Declares the legacy private mount-entry parser API.

## API Surface

- `struct my_mntent` mirrors core libc `mntent` fields using owned strings and integer dump/pass fields.
- `mntFILE` stores file pointer, filename, line number, and hard/soft parse error counters.
- Declares open, close, append, and read functions.

## Dependencies And Risks

No include guard around required `FILE` definition is provided here, so including source files must already include `<stdio.h>` or equivalent. Callers must free strings obtained through parsed entries after copying or storing them.
