# sources/distributed-fs/ceph-client/scripts/checkversion.pl

## Purpose
`checkversion.pl` enforces include hygiene for `<linux/version.h>`. It reports files that use version macros without including the header, and files that include the header without using any version macro.

## Important APIs, Types, and Functions
This is a single-pass Perl scanner over argv files. It skips generated UAPI version header paths. It tracks `$fInComment`, `$fInString`, `$fUseVersion`, and `$iLinuxVersion`. It recognizes quoted and angle-bracket includes and version uses including `LINUX_VERSION_CODE`, `KERNEL_VERSION`, and major, patchlevel, or sublevel macros.

## Control Flow and State
For each file, the script strips C comments and string literals using regex state across lines before looking for preprocessor includes and macro references. Once it sees both an include and a use it can stop scanning. It prints diagnostics after closing each file. State is per file only.

## Dependencies and Integration
It depends only on Perl and source file arguments, and is intended for kernel tree checks run by developers or build scripts.

## Risks and Test Signals
The lexer is deliberately lightweight and can be confused by unusual C syntax, preprocessor-generated tokens, raw strings in non-C files, or macros split across lines. Test with files containing block comments across lines, quoted macro names, both include styles, generated paths, and unused include cases.
