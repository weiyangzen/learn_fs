# sources/distributed-fs/openafs/src/vlserver/Makefile.in

## Purpose

`Makefile.in` builds the OpenAFS volume location server components, generated VL RPC stubs, helper utilities, static/shared VLDB libraries, and installable headers. It wires RXGEN, COMPILE_ET, Ubik/RX/auth dependencies, and install/dest targets for `vlserver`, `vlclient`, `cnvldb`, and `vldb_check`.

## Important Targets And Variables

- `INCLS`, `LIBS`, `LT_objs`, and `LT_deps` define compile/link dependencies.
- `all` builds servers/tools, generated stubs, `liboafs_vldb.la`, `libvlserver_pic.la`, `libvldb.a`, and `depinstall`.
- `generated` produces `vl_errors.c`, `vlserver.h`, RX client/server/XDR sources, and headers from `vldbint.xg` and `vl_errors.et`.
- RXGEN rules create `vldbint.cs.c`, `vldbint.ss.c`, `vldbint.xdr.c`, `vldbint.h`, `Kvldbint.cs.c`, and `Kvldbint.xdr.c`.
- `install` and `dest` install binaries conditionally when pthreaded Ubik is not enabled, but always install libraries and public headers.
- `clean` removes generated/object/archive/binary artifacts.

## Control Flow

Build flow starts from generated RPC/error-table sources, compiles server/client/tool objects against VL headers, links utilities with LWP Ubik/RX/auth libraries, then stages generated headers into top-level include directories via `depinstall`. Install flow creates server sbin/lib/include directories and places versioned artifacts into either configured destinations or legacy `DEST` paths.

## State And Persistence Behavior

This file does not manage runtime state, but it controls which generated protocol artifacts and conversion/checking tools are available. Installing `cnvldb` as `vldb_convert` and `vldb_check` is important for VLDB persistence migration and validation workflows.

## Dependencies And Integration Points

It includes shared config makefiles, LWP make rules, RXGEN, COMPILE_ET, roken, XLIBS, Ubik, auth, RXKAD, RXSTAT, command, audit, util, and crypto libraries. It exports headers under `afs/` for clients like `viced.c` and `vlclient.c`.

## Risks And Edge Cases

- `all` lists `vlserver` and `cnvldb` twice, which is harmless but noisy.
- Install skips server binaries when `ENABLE_PTHREADED_UBIK=yes`; packaging must ensure an alternate pthreaded build installs equivalent binaries.
- Generated-file dependency order matters; stale RXGEN outputs can create protocol mismatches.

## Test Signals

Run clean builds, generated-only builds, `make install DESTDIR=...`, pthreaded and non-pthreaded Ubik variants, and ABI checks that installed `vl_opcodes.h`, `vlserver.h`, `vldbint.h`, and `cnvldb.h` match the build outputs.
