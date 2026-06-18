# sources/compression/lz4/lib/liblz4-dll.rc.in

## Purpose
This Windows resource template embeds version and product metadata into the LZ4 DLL.

## Important Fields
The template includes `<windows.h>` and defines a `VERSIONINFO` block. Placeholders `@LIBVER_MAJOR@`, `@LIBVER_MINOR@`, `@LIBVER_PATCH@`, and `@LIBLZ4@` populate `FILEVERSION`, `PRODUCTVERSION`, `FileVersion`, `InternalName`, `OriginalFilename`, and `ProductVersion`. String metadata includes company, description, copyright, product name, and translation.

## Control Flow
It is not executed directly. `lib/Makefile` replaces placeholders with `sed` to create `liblz4-dll.rc`, then compiles that resource to `liblz4-dll.o` with `windres` for inclusion in the DLL link.

## State and Persistence
The template is source state. Generated persistent artifacts are the substituted `.rc` file and compiled resource object during Windows builds.

## Dependencies and Integration Points
It depends on Windows resource compiler syntax and Makefile substitution. It integrates with DLL metadata visible in Windows file properties and installers.

## Risks
Metadata can drift if copyright years, company naming, or product descriptions change. Placeholder substitution must replace all values; unresolved placeholders would ship visibly in DLL metadata.

## Test Signals
On a Windows build, inspect generated `liblz4-dll.rc`, verify `windres` succeeds, and check the built DLL's version resource with a resource viewer or file properties.
