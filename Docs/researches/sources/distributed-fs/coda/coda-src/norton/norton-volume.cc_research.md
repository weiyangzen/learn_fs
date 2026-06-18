# sources/distributed-fs/coda/coda-src/norton/norton-volume.cc

Purpose: implements volume listing, lookup, display, delete marking, index lookup, detail printing, and rename commands for Norton.

APIs and flow: `GetVol` by ID/name and `GetVolIndex` scan `VolByIndex` up to `GetMaxVolId`/`MAXVOLS`, filtering by `VOLUMEHEADERMAGIC`. Display functions print header and `VolumeDiskData` fields. `delete_volume` sets `destroyMe` to `0xD3` in an RVM transaction. `rename_volume` writes a fixed-size zero-padded name in an RVM transaction. Parser wrappers choose ID vs name based on `Parser_uint`.

State/dependencies: depends on recoverable volume storage and `norton-recov.cc`. Mutations persist in RVM. Risks include destructive operator commands, no duplicate-name checks on rename, no transaction status handling beyond minimal reporting, and date formatting using `tm_year` directly. Test signal is interactive volume commands and reinit workflows.
