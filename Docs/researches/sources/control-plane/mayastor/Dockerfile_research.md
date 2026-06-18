# sources/control-plane/mayastor/Dockerfile

## Purpose
Builds a Nix-based Mayastor development/CI environment image with dependencies pre-downloaded and prebuilt for nightly and stable channels.

## Important Instructions
Starts from `nixos/nix`, sets `NIX_EXPR_DIR=/tmp/nix-expr`, adds `nixpkgs-unstable`, installs `bash git nano sudo procps`, copies `shell.nix` and `nix`, then runs `nix-shell --argstr channel nightly` and `nix-shell --argstr channel stable`.

## Control Flow
Docker builds layers in order: Nix channel setup, base tools, copy Nix expressions, pre-populate debug and release dependency shells.

## State and Persistence
Persists Nix store contents and installed tools inside the image. Does not include full source tree, only Nix expressions.

## Dependencies and Integration Points
Depends on Nix channel availability and repo Nix expressions. Used by CI/CD pipeline and development to avoid repeatedly resolving/building dependencies.

## Risks
`nixpkgs-unstable` is mutable unless pinned elsewhere by shell.nix inputs, so rebuilds can drift. Prebuilding both channels can be expensive. The image includes sudo and editor utilities, increasing size.

## Test Signals
Build the Dockerfile and run `nix-shell --argstr channel nightly --run "cargo --version"` or equivalent dependency checks inside the image.
