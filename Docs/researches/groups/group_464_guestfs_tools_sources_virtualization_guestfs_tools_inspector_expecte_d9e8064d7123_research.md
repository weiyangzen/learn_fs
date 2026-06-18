# Group Research: group_464_guestfs_tools_sources_virtualization_guestfs_tools_inspector_expecte_d9e8064d7123

Scope: `Docs/research_subset_a.md` only. Files read completely: 30 guestfs-tools files covering `virt-inspector`, `virt-log`, `virt-ls`, `virt-make-fs`, shared C helpers, OCaml build wrappers, gettext/po4a build glue, POD option checking, and expected inspector XML fixtures.

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-fedora.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-fedora.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Fedora guest image. It validates the complete inspector serialization path for a Fedora-like Linux guest.

## Contents

The document has one `<operatingsystem>` under `<operatingsystems>`. It identifies root `/dev/VG/Root`, Linux `x86_64`, distro `fedora`, product `Fedora release 14 (Phony)`, version `14.0`, RPM/yum packaging, hostname `fedora.invalid`, and osinfo ID `fedora14`.

It records two mountpoints: `/dev/VG/Root` mounted at `/`, and `/dev/sda1` mounted at `/boot`. It records two ext2 filesystems with labels `ROOT` and `BOOT` and deterministic UUIDs.

The large body is an `<applications>` list with 172 RPM application entries. Entries include package metadata fields such as `name`, optional `epoch`, `version`, `release`, `arch`, `url`, `summary`, and multiline `description`. The list exercises stable ordering and rich RPM metadata extraction, including packages from base system utilities through systemd, rpm, glibc, kernel/core boot packages, and ending with `zlib`.

## Research Notes

This file is not executable code; it is a regression oracle. It is especially important because it checks that `virt-inspector` emits package descriptions, summaries, architecture, release, epoch, filesystem labels, UUIDs, and canonicalized device names exactly as expected.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-fedora.img.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-ubuntu.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-ubuntu.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Ubuntu guest image.

## Contents

The document describes one Linux `x86_64` Ubuntu guest rooted at `/dev/sda2`. It reports product `Ubuntu 10.10 (Phony Pharaoh)`, version `10.10`, package format `deb`, package management `apt`, hostname `ubuntu.invalid`, and osinfo ID `ubuntu10.10`.

It records mountpoints for `/` on `/dev/sda2` and `/boot` on `/dev/sda1`. The filesystems section includes `/dev/mapper/cryptswap1` with no type/label/UUID metadata, `/dev/sda1` as ext2 with label `BOOT`, and `/dev/sda2` as ext2 with a deterministic UUID.

The applications section contains three Debian-style test packages, each with `source_package`, URL, summary, and multiline description.

## Research Notes

This fixture verifies Debian package metadata handling, swap-like block devices with sparse filesystem metadata, and Ubuntu-specific inspector fields.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-ubuntu.img.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-windows.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-windows.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Windows guest image.

## Contents

The document describes one Windows guest rooted at `/dev/sda2`. It reports `name` and `distro` as `windows`, architecture `i386`, product `Microsoft Windows 7 Phony Edition`, product variant `Client`, version `6.1`, systemroot `/Windows`, current control set `ControlSet001`, hostname `windows.invalid`, and osinfo ID `win7`.

It records a single `/` mountpoint and NTFS filesystem on `/dev/sda2` with UUID `091A29CC586B609C`. It also includes one drive mapping, `C` to `/dev/sda2`.

The applications section has four Windows application entries. These exercise registry-derived fields including display name, version, URL, install path, publisher, description, and WOW6432Node-style 32-bit application detection.

## Research Notes

This fixture validates the Windows-specific branches in inspector output: registry-derived identity, current control set, drive mappings, NTFS metadata, and application metadata.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-windows.img.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/inspector.c -->
# File Research: sources/virtualization/guestfs-tools/inspector/inspector.c

## Role

C implementation of `virt-inspector`, the tool that inspects disk images or libvirt guests and emits structured XML describing detected operating systems, filesystems, mountpoints, drive mappings, installed applications, and optional icons.

## Major Responsibilities

The program creates a global libguestfs handle, parses common guestfs options, adds drives, launches the appliance, decrypts inspected devices when keys are provided, runs `guestfs_inspect_os`, and writes XML to stdout.

Supported command-line behavior includes `-a`, `-d`, `--connect`, `--format`, `--blocksize`, LUKS key options, `--no-applications`, `--no-icon`, tracing/verbose/version/help, and a modal `--xpath` mode. Old-style syntax is preserved by treating path-like arguments as image files and other arguments as domain names.

## XML Output

The output path uses libxml2 writer macros. For each root, it canonicalizes the root device, emits OS type, architecture, distro, product name/variant, major/minor version, package format/manager, Windows systemroot/current control set/group policy where available, hostname, optional build ID, osinfo ID, mountpoints, filesystems, drive mappings, applications, and optional base64 icon data.

Mountpoints are sorted by path length then name. Filesystems are sorted by device name. Drive mappings are sorted case-insensitively. Application output includes all populated `guestfs_application2` fields.

## XPath Mode

`--xpath` reads XML from stdin, evaluates the supplied XPath expression, and prints node-set, string, or scalar results. This mode forbids disk/domain options and exits after processing.

## Research Notes

The file is mostly glue over libguestfs inspection APIs, but it is the canonical definition of the XML schema shape consumed by the expected `*.img.xml` fixtures.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/inspector.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-docs.sh

## Role

Documentation coverage test for `virt-inspector`.

## Behavior

The script sources `../tests/functions.sh`, enables `set -e` and `set -x`, honors `skip_if_skipped`, then runs top-level `podcheck.pl` against `virt-inspector.pod` and the `virt-inspector` tool name. It passes `--path $top_srcdir/common/options` so POD include directives for shared options can be resolved.

## Research Notes

This test ensures command-line options reported by the binary remain documented in the man page and help output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-luks-on-lvm.sh -->
# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-luks-on-lvm.sh

## Role

Regression test for `virt-inspector` on a Fedora phony guest with LUKS volumes layered on LVM.

## Behavior

The test requires libguestfs minor version at least 47 and skips empty image files. It defines three key selector sets: direct `/dev/Volume-Group/...` paths, escaped `/dev/mapper/...` paths, and repeated `all:key:` selectors.

For `fedora-luks-on-lvm.img`, it obtains the root LUKS UUID with `guestfish`, runs `virt-inspector` with raw format and explicit keys, validates the output against `virt-inspector.rng`, substitutes `ROOTUUID` into the expected XML, and diffs. It reruns with mapper-style keys and all-selector keys, diffing each output against the first actual XML.

## Research Notes

This is focused on encrypted-device selector compatibility and stable XML output once decryption succeeds.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-luks-on-lvm.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-lvm-on-luks.sh -->
# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-lvm-on-luks.sh

## Role

Regression test for `virt-inspector` on a Fedora phony guest with LVM layered on LUKS.

## Behavior

After common test setup and skip handling, the script targets `fedora-lvm-on-luks.img`. If the image is non-empty, it pipes the `FEDORA` passphrase to `virt-inspector --keys-from-stdin --format=raw -a`, writes `actual-$b.xml`, validates the XML against the Relax NG schema, and diffs it against the expected XML with `$diff_ignore`.

## Research Notes

This validates stdin-based key handling for encrypted images and checks that inspector output remains deterministic.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-lvm-on-luks.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector.sh -->
# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector.sh

## Role

Main regression test for `virt-inspector` phony guest images.

## Behavior

The script defines a `diff_ignore` pattern to ignore Windows NTFS UUID differences because ntfs-3g cannot always set them deterministically. It loops over Debian, Fedora, Ubuntu, Arch Linux, CoreOS, and Windows phony images. For each non-empty image, it runs `virt-inspector --format=raw -a`, validates output with `xmllint --relaxng virt-inspector.rng`, and diffs against the corresponding expected XML.

A commented mdadm two-disk Fedora test is present but disabled because mdadm support is problematic for many users.

## Research Notes

This test is the broadest golden-output guard for inspector XML across Linux and Windows guests.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-virt-inspector.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-xmllint.sh -->
# File Research: sources/virtualization/guestfs-tools/inspector/test-xmllint.sh

## Role

Schema validation test for checked-in example XML files.

## Behavior

The script sources the common test functions, enables strict/trace shell mode, honors skips, and runs `$XMLLINT --noout --relaxng $srcdir/virt-inspector.rng` for every `$srcdir/example-*.xml`.

## Research Notes

Unlike the phony-image tests, this validates static example XML files, ensuring documentation/sample outputs remain compatible with the inspector Relax NG schema.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/test-xmllint.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/lib/guestfs-internal-all.h -->
# File Research: sources/virtualization/guestfs-tools/lib/guestfs-internal-all.h

## Role

Shared internal header for definitions used across all libguestfs C code, including daemon, library, bindings, and virt tools.

## Contents

The header defines GCC compatibility helpers, `ATTRIBUTE_UNUSED`, string comparison macros such as `STREQ`, `STRPREFIX`, and `STRSUFFIX`, `MAX`/`MIN`, `SOCK_CLOEXEC` fallback, and Apple XDR naming compatibility.

It provides `ADD_ARG`, a bounded helper macro for building short argv arrays with abort-on-overflow behavior.

It defines `is_zero`, an inline zero-buffer test that checks up to the first 16 bytes and then compares the rest of the buffer to the first 16-byte window.

It also defines `COMPILE_REGEXP`, a constructor/destructor macro for compiling PCRE2 regexes at load time and freeing them at unload time.

Finally it declares `mountable_type_t` with device, btrfs subvolume, and already-mounted path variants.

## Research Notes

This file centralizes low-level portability and utility macros that many tools rely on indirectly.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/lib/guestfs-internal-all.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/log/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/log/Makefile.am

## Role

Automake build file for `virt-log`.

## Contents

It distributes `test-docs.sh`, `test-virt-log.sh`, and `virt-log.pod`; builds the `virt-log` binary from `log.c`; sets include paths for common utilities, structs, options, Windows helpers, libguestfs headers, and gnulib; and links against common options/structs/utils libraries, libguestfs, libxml2, libvirt, gettext, and gnulib.

It defines manpage and website HTML generation through `$(PODWRAPPER)` using GPLv2+ metadata and safe warnings. Test execution uses `$(top_builddir)/run --test` and runs the docs and functional tests. It also provides a `check-valgrind` wrapper.

## Research Notes

The file follows the standard guestfs-tools C utility build pattern.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/log/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/log/log.c -->
# File Research: sources/virtualization/guestfs-tools/log/log.c

## Role

C implementation of `virt-log`, a read-only tool for displaying log files from an inspected virtual machine.

## Major Responsibilities

The program parses standard guestfs options, adds drives, launches libguestfs, mounts the single inspected root, and chooses a log extraction strategy based on guest type.

For Windows guests, it supports only Vista-or-newer event logs and delegates to `do_log_windows_evtx`. For Linux guests, it prefers a systemd journal under `/var/log/journal`; otherwise it tries `/var/log/syslog` and `/var/log/messages`.

## Linux Journal Output

`do_log_journal` opens the journal through guestfs APIs, iterates entries, extracts fields from xattrs, formats realtime timestamps as `"%b %d %H:%M:%S"`, prints identifier or command, PID, syslog priority name, and message. Priority defaults to info.

## Text And Windows Logs

Text logs are streamed directly with `guestfs_download` to `/dev/stdout`.

Windows EVTX support requires host `evtxdump.py`. The tool locates `System.evtx` case-sensitively, downloads it to a temporary file because python-evtx needs mmap-able input, then invokes `evtxdump.py` and reports process status failures.

## Research Notes

The implementation is intentionally read-only and inspector-driven. Its main risk surface is dependence on host external tooling for Windows EVTX parsing.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/log/log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/log/test-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/log/test-docs.sh

## Role

Documentation coverage test for `virt-log`.

## Behavior

The script uses the common test harness, strict/trace shell mode, skip handling, and runs `podcheck.pl "$srcdir/virt-log.pod" virt-log --path $top_srcdir/common/options`.

## Research Notes

It verifies option parity among the binary, help output, and POD documentation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/log/test-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/log/test-virt-log.sh -->
# File Research: sources/virtualization/guestfs-tools/log/test-virt-log.sh

## Role

Functional smoke test for `virt-log` on phony guest images.

## Behavior

The script defines `can_handle`, which requires journal availability for `fedora.img` and allows other images. It creates a temporary output file, loops over Fedora, Debian, and Ubuntu phony images, skips empty or unsupported images, runs `$VG virt-log --format=raw -a "$f"` capturing stdout/stderr, prints the captured log output, and removes the temporary file.

## Research Notes

This is a smoke test rather than a golden diff test. It exercises log extraction paths while tolerating fixture/environment variation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/log/test-virt-log.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ls/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/ls/Makefile.am

## Role

Automake build file for `virt-ls`.

## Contents

It distributes `test-docs.sh`, `test-virt-ls.sh`, and `virt-ls.pod`; builds `virt-ls` from `ls.c`; sets include paths for common utilities, structs, visit traversal helpers, options, Windows helpers, libguestfs headers, and gnulib; and links the common libraries plus libguestfs, libxml2, libvirt, gettext, and gnulib.

It generates `virt-ls.1` and website HTML with `$(PODWRAPPER)` and registers the documentation and functional tests under `$(top_builddir)/run --test`.

## Research Notes

The key distinction from nearby C tools is the extra dependency on `common/visit` for recursive `-lR` traversal.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ls/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ls/ls.c -->
# File Research: sources/virtualization/guestfs-tools/ls/ls.c

## Role

C implementation of `virt-ls`, a read-only guest filesystem listing tool.

## Major Responsibilities

The program parses drive/domain/mount options and listing flags, launches libguestfs, mounts either explicit mountpoints or the inspected root, and lists one or more guest directories.

It supports four listing modes: plain `ls`, long `-l`, recursive `-R`, and long-recursive `-lR`. Many advanced flags are restricted to `-lR`: CSV output, human-readable sizes, UID/GID output, times, relative/day/time_t time formats, extra stat fields, and checksums.

## Listing Behavior

Plain mode calls `guestfs_ls`. Long mode calls `guestfs_ll`. Recursive mode calls `guestfs_find`. Long-recursive mode uses the shared `visit` helper and `show_file`, which receives statns and xattrs for each entry.

`show_file` emits file type, permissions, size, optional UID/GID, optional atime/mtime/ctime, optional device/inode/link/rdev/block fields, optional checksum for regular files, full path, and symlink target.

## Output Formatting

Output supports space-separated and CSV formats. CSV quoting is implemented locally for spaces, quotes, newlines, and commas. Size output can use gnulib `human_readable`. Device numbers are printed as major:minor. Time output can be formatted wall-clock, raw seconds, seconds before now, or days before now.

## Research Notes

This file is the core formatting implementation for `virt-ls`; tests cover both plain `/bin` output and selected `-lR` fields.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ls/ls.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ls/test-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/ls/test-docs.sh

## Role

Documentation coverage test for `virt-ls`.

## Behavior

The script runs `podcheck.pl` against `virt-ls.pod` and `virt-ls`, passing the shared options path. It ignores aliases/options `--checksums`, `--extra-stat`, `--time`, and `--uid`, which are accepted by the tool but intentionally handled specially for documentation parity.

## Research Notes

This keeps the rich `virt-ls` option surface synchronized with its POD and help output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ls/test-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ls/test-virt-ls.sh -->
# File Research: sources/virtualization/guestfs-tools/ls/test-virt-ls.sh

## Role

Functional regression test for `virt-ls`.

## Behavior

The script first checks exact plain listing output for `/bin` in the Fedora phony image. Expected names are `ls`, `rpm`, `sh`, and `test1` through `test7`.

It then checks `virt-ls -lR` on `/boot`, piping through `awk` to compare selected columns: file type/permissions, size field, and path. The expected tree includes `/boot`, `/boot/grub`, `grub.conf`, an initramfs, `lost+found`, and a vmlinuz file.

Finally it invokes old-style `virt-ls -l` and `virt-ls -R` syntaxes against the Fedora image as smoke checks.

## Research Notes

The test validates both modern option syntax and legacy positional image syntax.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ls/test-virt-ls.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/make-fs/Makefile.am

## Role

Automake build file for `virt-make-fs`.

## Contents

It distributes `test-virt-make-fs.sh`, `test-virt-make-fs-docs.sh`, and `virt-make-fs.pod`; builds `virt-make-fs` from `make-fs.c`; includes common utils, structs, options, fish headers, libguestfs headers, and gnulib; and links against common libraries, libguestfs, libxml2, gettext, and gnulib.

It generates the man page and website HTML through `$(PODWRAPPER)` with GPLv2+ metadata and safe warnings. Tests include the docs test and the randomized filesystem creation test.

## Research Notes

Despite the header comment saying `virt-diff`, this Makefile builds `virt-make-fs`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/make-fs.c -->
# File Research: sources/virtualization/guestfs-tools/make-fs/make-fs.c

## Role

C implementation of `virt-make-fs`, which creates a disk image containing a filesystem populated from a directory, tar archive, or compressed tar archive.

## Major Responsibilities

The tool parses output format, filesystem type, partitioning, label, size, floppy shortcut, block size, verbose/debug, version, and tracing options. It expects exactly `input output.img`.

It estimates input size, adds overhead for partition alignment, filesystem metadata, journals, btrfs metadata, xfs minimum size, and a 10% margin, then creates the output disk with `guestfs_disk_create_argv`. For qcow2 it requests metadata preallocation.

## Input Handling

Directories are measured with `du --apparent-size -b -s` and later converted to tar through a background `tar -C input -cf - .`. Non-directories are classified with `file -bsSLz`; plain tar files use file size, while compressed tar archives are decompressed through `uncompress`, `gzip`, `bzip2`, or `xz` to count bytes and later feed `guestfs_tar_in` through `/dev/fd`.

## Filesystem Creation

The tool can create raw or partitioned images. Partitioned images call `guestfs_part_disk` and set known MBR type IDs for FAT, NTFS, ext, and minix. Non-btrfs filesystems use `guestfs_mkfs_opts_argv`; btrfs uses `guestfs_mkfs_btrfs_argv` with single data/metadata profiles. VFAT mounts with `utf8`.

## Research Notes

The implementation coordinates host subprocesses and libguestfs operations. Failure paths keep the output image under cleanup control until the function completes successfully.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/make-fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs-docs.sh

## Role

Documentation coverage test for `virt-make-fs`.

## Behavior

The script runs `podcheck.pl "$srcdir/virt-make-fs.pod" virt-make-fs --ignore=--debug` after common setup and skip handling.

## Research Notes

`--debug` is accepted for compatibility with the old Perl tool and is intentionally ignored in documentation parity checks.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs.sh -->
# File Research: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs.sh

## Role

Randomized functional test for `virt-make-fs`.

## Behavior

The script queries appliance feature availability with Perl `Sys::Guestfs` for ntfs3g, ntfsprogs, and btrfs. It builds random choices for filesystem type, image format, partition mode, extra size, label, and block size. Btrfs can be disabled with `SKIP_TEST_VIRT_MAKE_FS_BTRFS`; vfat is excluded because tar ownership restoration fails on FAT.

It creates a random zero-filled test file up to 8191 KiB, tars it, invokes `$VG virt-make-fs` with the random parameters, and removes the generated tar and output image.

## Research Notes

This is Monte Carlo-style coverage for combinations of filesystem type, partitioning, format, label, size, and sector size.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ocaml-dep.sh.in -->
# File Research: sources/virtualization/guestfs-tools/ocaml-dep.sh.in

## Role

Configure-time template for generating `.depend` files for OCaml subdirectories.

## Behavior

The script wraps `ocamldep -all -one-line`. It defines shared OCaml include directories, derives relative source/build paths with configured `realpath`, builds include flags for the current subdir plus common OCaml libraries, writes `.depend-t`, rewrites absolute source paths into build-relative dependency targets with `sed`, marks the temporary file read-only, and renames it to `.depend`.

## Research Notes

The path rewriting is the important behavior: generated objects and `_config.ml` files are redirected to builddir locations while source references remain relative and stable for Automake includes.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ocaml-dep.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/ocaml-link.sh.in -->
# File Research: sources/virtualization/guestfs-tools/ocaml-link.sh.in

## Role

Configure-time template used to link OCaml programs in Automake builds.

## Behavior

The script accepts an optional `-cclib`/`--cclib` argument, requires `--` before the command, and then executes the supplied OCaml link command with configured runtime PIC option, `-linkpkg`, and `-cclib "@LDFLAGS@ $cclib"` placed last.

If Automake verbose mode is enabled, it echoes the full command before executing it.

## Research Notes

The script exists because Automake cannot otherwise place `-cclib` at the required end of the OCaml linker command line.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/ocaml-link.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/po-docs/Makefile.am

## Role

Top-level Automake file for translated guestfs-tools man pages and POD files.

## Contents

It reads languages from `LINGUAS` while avoiding the uppercase `LINGUAS` environment conflict, and currently treats `ja` and `uk` as translated language subdirectories. It distributes the docs POT file, all language `.po` files, and the generated `podfiles` list.

The `guestfs-tools-docs.pot` target runs `PO4A_UPDATEPO` over all POD files listed in `podfiles`. The `podfiles` target finds repository `.pod` files, excludes Debian, release-note, po-docs, and stamp files, appends Perl POD files from `po/POTFILES-pl`, sorts, and writes the list.

## Research Notes

The file notes the po4a integration is naive and separate from the main `po/` domain.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/ja/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/po-docs/ja/Makefile.am

## Role

Japanese translated documentation subdirectory Makefile.

## Contents

The file intentionally contains no local logic beyond comments and `include $(srcdir)/../language.mk`.

## Research Notes

All language-specific translated manpage generation is centralized in `po-docs/language.mk`. This file is expected to be identical to other translated language subdirectory Makefiles.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/ja/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/language.mk -->
# File Research: sources/virtualization/guestfs-tools/po-docs/language.mk

## Role

Shared Automake logic for each translated documentation language.

## Contents

It derives `LINGUA` from the current directory name, cleans generated `.pl` and `.pod` files, defines the translated manpage set for guestfs tools, and distributes both translated manpages and generated POD files.

`all-local` builds all manpages. Special `PODWRAPPER` rules handle inserted snippets for `virt-builder`, `virt-customize`, and `virt-sysprep`; the generic `%.1: %.pod` rule handles other tools.

The `%.pod` rule runs `PO4A_TRANSLATE` using the language `.po`, selects the original POD path from `po-docs/podfiles`, writes a temporary translated POD, removes po4a’s unwanted header up through `=encoding`, and leaves the cleaned POD. The install hook places translated `.1` pages under `$(mandir)/$(LINGUA)/man1`.

## Research Notes

This file is the core translated documentation build pipeline.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/language.mk -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/uk/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/po-docs/uk/Makefile.am

## Role

Ukrainian translated documentation subdirectory Makefile.

## Contents

Like the Japanese version, this file is deliberately minimal and includes `$(srcdir)/../language.mk`.

## Research Notes

The comments state all `po-docs/$lang/Makefile.am` files should be identical, with real behavior centralized in `language.mk`.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/po-docs/uk/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/po/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/po/Makefile.am

## Role

Main gettext Automake file for guestfs-tools program translations.

## Contents

It defines gettext domain `$(PACKAGE_NAME)`, copyright holder, Bugzilla msgid address, language list from `LINGUAS`, source file lists from `POTFILES`, `POTFILES-pl`, and `POTFILES-ml`, and generated `.po`/`.gmo` files.

When GNU gettext is available, it defines `XGETTEXT_ARGS` for C-style and Perl extraction, fixes placeholder charset values to UTF-8, optionally extracts OCaml strings through `OCAML_GETTEXT`, runs `xgettext` over C and Perl file lists, and emits `$(DOMAIN).pot`.

The `.po.gmo` rule compiles translations with `msgfmt`. The install hook installs `.mo` files under `$(datadir)/locale/$lang/LC_MESSAGES/$(DOMAIN).mo`.

## Research Notes

This is separate from `po-docs`; it covers translatable UI/program strings rather than manpage/POD translations.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/po/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/podcheck.pl -->
# File Research: sources/virtualization/guestfs-tools/podcheck.pl

## Role

Perl test utility that compares a tool’s real command-line options with its POD documentation and `--help` output.

## Behavior

The script accepts `input.pod tool` plus options: `--ignore`, `--insert`, `--verbatim`, and `--path`. It slurps the POD, applies explicit insertions, resolves `__INCLUDE:*.pod__` through optional search paths, applies verbatim insertions, and resolves `__VERBATIM:*.txt__`.

It runs the target tool with `--long-options`, `--short-options`, and `LANG=C --help`. Tool option names become the authoritative set, with a few automatic ignores such as `--color`, `--colour`, and `--debug-gc`.

It then checks that every non-ignored tool option appears as a POD `=item ... B<--option>` entry, checks that POD does not document unknown options except for a few removed subscription-manager options, and checks that help output mentions exactly the known options, ignoring `--options` as a synopsis placeholder.

## Research Notes

This script is the shared enforcement mechanism used by the docs tests in this group. It supports podwrapper-like preprocessing so generated manpage content can still be checked at source-test time.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/podcheck.pl -->