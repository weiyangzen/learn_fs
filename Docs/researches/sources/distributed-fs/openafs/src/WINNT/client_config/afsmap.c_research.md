# sources/distributed-fs/openafs/src/WINNT/client_config/afsmap.c

## Purpose
`afsmap.c` is intended to be a small command-line tool for listing, adding, deleting, and persisting AFS drive mappings. It parses drive letters, AFS paths, UNC paths, optional submounts, and `/persistent`, then calls drive-map helpers.

## Important APIs, Types, and Functions
The file contains `usage` and `main`. It uses `MountDOSDrive`, `DisMountDOSDrive`, `WriteActiveMap`, `DriveIsGlobalAfsDrive`, `IsValidSubmountName`, `lana_GetNetbiosName`, and registry reads for `MountRoot`.

## Control Flow
`main` validates argument count, handles `/list` and `/help`, parses a drive letter, handles `/delete`, reads mount root and NetBIOS server name, then branches between UNC-style paths and AFS mount-root paths. UNC inputs are mapped directly by extracting the submount portion after `\\netbios\`. AFS paths optionally generate or accept a submount and persist the active-map flag.

## State and Persistence Behavior
The tool changes live Windows network drive mappings through `MountDOSDrive` and `DisMountDOSDrive`, and records desired active state with `WriteActiveMap`. It consults the service-parameter registry for the configured mount root and the SMB server name from LANA helper code.

## Dependencies and Integration Points
This file is a CLI-facing integration point for the same drive-mapping backend used by the GUI. It depends on OpenAFS fs utilities, rxkad headers, Win32 registry APIs, and the LANA/NetBIOS helper stack.

## Risks and Edge Cases
The current code has multiple apparent defects: it references `program` instead of `argv[0]`, uses `stricmp` tests as though zero means false in some branches, indexes `argv[2]`/`argv[3]` without proving they exist, mixes `cm_mountRoot` names with local `mountRoot`, and passes bad arguments to `strncpy`. These make this file high risk unless it is dead or excluded from the build. Path comparisons also appear to use `argv[1]` where `argv[3]` was intended.

## Test Signals
Tests should cover `/help`, `/list`, add/delete with bad arity, invalid drives, global-drive deletion refusal, UNC path parsing, AFS path parsing with generated and explicit submounts, and persistent flag storage. Static analysis or a build of this target should be treated as a primary signal because the source has compile-time-looking errors.
