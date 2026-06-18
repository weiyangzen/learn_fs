<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic -->
# sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic

## Purpose
Decodes macOS kernel panic logs that reference the OpenAFS kernel extension and produces a symbolized crash dump. It locates the latest complete panic section, extracts the OpenAFS load address, kernel version, slide, and backtrace addresses, prepares kext/kernel symbol files, drives `gdb`, and writes a readable dump under `/var/db/openafs/logs` by default.

## Important APIs, Types, And Functions
The script is Perl using `Getopt::Long`, `File::Temp`, `IO::File`, `File::Basename`, `Pod::Usage`, and `bigint`. Main helpers are `read_panic`, `extract_openafs`, `extract_kernel`, `generate_symbol_files`, `write_gdb_input_file`, and `write_dump_file`. External tools are `gdb`, `kextload` or `kextutil`, optional `dmgutil`/`hdutil`, `gzcat`, `pax`, and `cp`. Options select panic input, dump output, kernel image, system extension path, debug-kit archive, OpenAFS package archive, DMG utility, quiet/verbose modes, and help.

## Control Flow
Startup validates required programs and the panic file, parses crash metadata, maps the kernel version string to `gdb` and kext architectures, optionally extracts matching kernel/debug and OpenAFS kext artifacts from DMGs, generates symbol files at the adjusted OpenAFS load address, writes `gdb` commands that subtract the kernel slide from each backtrace address, runs `gdb -batch`, and writes the dump. `read_panic` seeks to the last panic section, supports older PPC and Intel backtrace formats, scans loaded or unloaded kext lists for `org.openafs.filesystems.afs`, and records a warning if the module was unloaded.

## State And Persistence
Temporary state lives under an auto-cleaned `afsdebugXXXXXX` directory. Persistent output is only the requested crash dump file; the script creates its parent directory if needed and clobbers the target file. It reads system panic logs, installed kexts, optional KDK/OpenAFS archives, and kernel files but does not modify them except for copying kexts into the temp area when `kextutil` needs that layout.

## Dependencies And Integration Points
This is a Mac packaging/support utility installed into the OpenAFS tools bundle by `pkgbuild.sh.in`. It integrates with Apple's kext symbol tooling, historical Darwin panic-log formats, OpenAFS installer archive layout, and OpenAFS kernel extension bundle paths. Its output helps correlate panic PCs with OpenAFS source lines.

## Risks And Test Signals
Risks include stale assumptions about `/mach_kernel`, `gdb`, legacy panic formats, regex parsing of version strings, shell backticks with globbed DMG paths, and failures when modern macOS lacks kextload/gdb behavior expected by the script. Test signals are successful decoding of sample PPC/Intel panic logs, correct kernel-slide subtraction, valid kext symbol loading for `kextload` and `kextutil`, useful failure in quiet/non-quiet modes, and non-empty dump output with panic date, kernel version, OpenAFS version, and disassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic -->
