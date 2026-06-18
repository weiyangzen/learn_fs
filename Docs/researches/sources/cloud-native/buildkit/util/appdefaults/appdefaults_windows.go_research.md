# sources/cloud-native/buildkit/util/appdefaults/appdefaults_windows.go

## Purpose
Windows BuildKit default paths. It defines named-pipe Address, ProgramData-backed root/config, containerd CNI paths, and CDI spec directory.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `UserAddress, EnsureUserAddressDir, UserRoot, UserConfigDir, TraceSocketPath`.

## Control Flow, State, And Persistence
UserAddress returns Address and EnsureUserAddressDir is a no-op. UserCNIConfigPath and CDISpecDirs are package variables derived from environment variables at init time.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are ProgramData/ProgramFiles environment dependence and static init values. No local tests.
