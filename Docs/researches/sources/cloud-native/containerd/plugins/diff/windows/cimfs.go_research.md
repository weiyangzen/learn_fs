# sources/cloud-native/containerd/plugins/diff/windows/cimfs.go

## Purpose
Registers and implements Windows CimFS and block CIM diff appliers, importing OCI layer tar streams into CimFS-backed layer formats.

## Important APIs, Types, And Functions
Registers `cimfs` and `blockcim` diff plugins. `cimApplyFunc` abstracts import functions. `cimDiff.Apply` imports standard CimFS layers. `blockCIMDiff.Apply` imports block CIMs. `parseBlockCIMMount` decodes mount options. `applyCIMLayerCommon` handles content reading, processor chain, hashing, and descriptor return.

## Control Flow
Plugin init checks OS feature support, loads metadata content store, and returns the appropriate differ. Apply validates mount type, extracts source/parent/CIM paths and mount flags, builds an import function, then common code reads the blob, unwraps processors to an OCI layer, tees through a digest, invokes the import function, drains trailing data, and returns an OCI layer descriptor.

## State And Persistence
Writes CimFS or block CIM layer artifacts through hcsshim import APIs. Reads content blobs but does not write the content store. Parent layer paths come from mount options.

## Dependencies And Integration Points
Windows-only. Integrates with hcsshim CimFS APIs, containerd mount option helpers, content store, diff processors, and platform/plugin registration.

## Risks
Only single-file block CIM extraction is supported. Compare is not implemented. Mount option JSON parsing and parent path interpretation are critical. Host OS feature checks determine plugin availability.

## Test Signals
No direct tests in this subset. Coverage depends on Windows CimFS integration environments.
