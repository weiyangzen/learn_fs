# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile.go

Purpose: declares the `dockerfile` package at the frontend root.

Important APIs: none; the file only contains `package dockerfile`.

Control flow, state, and dependencies: no executable behavior or imports.

Integration: serves as a package anchor for sibling Dockerfile frontend integration tests that use `package dockerfile`.

Risks and test signals: no direct runtime risk. Removing it could affect package layout when only test files exist in the directory.
