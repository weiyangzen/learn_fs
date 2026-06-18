# sources/distributed-fs/openafs/src/tests/OpenAFS/CMU_copyright.pm

## Purpose
`CMU_copyright.pm` centralizes the Carnegie Mellon AFStools copyright and redistribution notice for the Perl test modules.

## Important APIs, types, and functions
It defines package `AFS::CMU_copyright` and returns true. There are no functions.

## Control flow
Loading the module only evaluates the copyright text and package declaration.

## State and persistence behavior
No runtime state or persistent effects are created.

## Dependencies and integration points
`OpenAFS::afsconf` imports this module to keep the license notice associated with the AFStools-derived Perl modules.

## Risks
The package namespace is `AFS::CMU_copyright`, while the file lives under `OpenAFS/`; this is intentional historical naming but can surprise module loaders.

## Test signals
Verify Perl can `use OpenAFS::CMU_copyright`/load the file through the harness and that dependent modules compile.
