# Research: sources/cloud-native/buildkit/executor/proxyca_linux.go

## Purpose
Linux proxy CA injection into build rootfs.

## Important APIs, Types, and Functions
`InjectProxyCA`, `firstCertificate`, `containsCertificate`, `removeInjectedCA`, `writeCertBundle`.

## Control Flow
Reads known CA bundle files, parses proxy cert, appends if absent, writes with preserved metadata, and returns cleanup to remove it.

## State and Persistence
Mutates temporary rootfs CA bundle files and later removes inserted cert content.

## Dependencies and Integration Points
Depends on Linux CA bundle paths, x509/pem parsing, and proxy namespace integration. Used when proxy capture needs trusted CA inside build containers.

## Risks and Edge Cases
Safe reversible mutation across distro bundle formats is the main risk.

## Test Signals
`proxyca_linux_test.go` covers insertion/detection/removal.
