
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/file.c

Purpose: implements EFI-stub file loading from `initrd=` and `dtb=` style command-line options, including same-volume lookup, optional text device-path lookup, concatenation of multiple files, chunked reads, and allocation under soft/hard limits.

Important APIs/types/functions: exports `handle_cmdline_files()`. Internals include `efi_open_file()`, `efi_open_volume()`, `find_file_option()`, and `efi_open_device_path()`. `struct finfo` combines `efi_file_info_t` with a bounded UTF-16 filename buffer.

Control flow: the loader applies load-option quirks, chooses firmware or built-in command lines depending on config, scans for the requested option prefix, resolves either an explicit EFI text device path or the kernel image volume, opens the file, obtains its size, grows a single EFI page allocation when concatenating files, reads data in 1 MiB chunks on x86 unless `efi=nochunk`, closes handles, and repeats for multiple occurrences and optional built-in second pass.

State and persistence behavior: the loaded files are returned as one contiguous EFI page allocation with address/size stored through caller pointers. Open file and volume protocol handles are transient. No durable state exists.

Dependencies and integration points: depends on EFI Simple File System, File Protocol, Device Path From Text Protocol, `efi_allocate_pages()`, `efi_free()`, load-option quirks, and config-command-line policy. It is used by initrd and DTB loading helpers.

Risks and test signals: filename parsing is bounded to 256 UTF-16 code units and stops on space/newline/NUL, so paths with spaces are unsupported. Chunked reads fix some firmware but break others, hence the `nochunk` option. Reallocation while concatenating must preserve prior file content and free old pages. Test signals include multiple initrd files, absolute EFI device paths, same-volume paths with `/` conversion to `\`, forced/extended built-in command lines, allocation failure unwinds, and corrupt read/error handling.
