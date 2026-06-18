# sources/compression/zlib/contrib/minizip/miniunz.c

Purpose: implements the `miniunz` demo command-line extractor/listing tool for MiniZip archives.

Important APIs/types/functions: helpers `change_file_date`, `mymkdir`, `makedir`, `do_banner`, `do_help`, `Display64BitsSize`, `do_list`, `do_extract_currentfile`, `do_extract`, `do_extract_onefile`, and `main`.

Control flow: `main` parses options for list, extract with paths, extract without paths, overwrite, password, and target directory. It opens the zip through Win32 or stdio I/O, appending `.zip` as a fallback. Listing reads global info and iterates entries printing sizes, method, ratio, date, CRC, and name. Extraction locates each entry, sanitizes leading slashes/dots and some `..` patterns, opens the current file with optional password, prompts for overwrite unless disabled, creates directories as needed, streams data through an 8 KiB buffer to disk, closes the current entry, and restores modification time.

State and persistence: creates directories and extracted files in the current or requested directory. Mutates `opt_overwrite` after an "All" prompt. Uses heap buffers for directory creation and extraction.

Dependencies/integration: depends on `unzip.h`, `ioapi`/`iowin32` indirectly, zlib constants, platform file APIs, and C runtime functions.

Risks: path sanitization is incomplete for robust zip-slip defense; it strips leading dots/slashes and adjusts to the last `..`, but crafted paths can still be subtle. `strncpy` truncation and `strcat(filename_try, ".zip")` have bounded but old-style handling. Interactive overwrite prompts make automation harder. Extraction trusts archive file metadata for timestamps.

Test signals: legacy `Makefile test` creates a text zip, lists it, extracts it, and compares content. Broader tests should include nested paths, Zip64 entries, encrypted files, overwrite modes, and malicious paths.
