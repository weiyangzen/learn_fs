# sources/cloud-native/moby/hack/generate-authors.sh

## Purpose
Regenerates the repository `AUTHORS` file from git history.

## Important APIs and Types
Computes `SCRIPTDIR` and `ROOTDIR`, then uses `git log --format='%aN <%aE>'` and `sort -uf`.

## Control Flow, State, and Persistence
The script overwrites `AUTHORS` with a generated header and unique sorted author identities, relying on `.mailmap` for normalization.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on a full enough git history and locale `C.UTF-8`. Risks include shallow clones omitting contributors, mailmap changes altering output, and generated-file churn. Validation is by rerunning the script and checking a clean diff.
