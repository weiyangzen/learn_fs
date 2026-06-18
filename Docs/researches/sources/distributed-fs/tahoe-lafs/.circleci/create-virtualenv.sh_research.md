## sources/distributed-fs/tahoe-lafs/.circleci/create-virtualenv.sh

Purpose: creates and bootstraps a virtualenv for CircleCI Docker images using a specified Python executable.

Important behavior: strict Bash mode, positional inputs `WHEELHOUSE_PATH`, `BOOTSTRAP_VENV`, and `PYTHON`, creation via `virtualenv --python`, then pip installs `certifi`, upgrades pip, upgrades setuptools/wheel, and installs `tox~=4.0`.

Control flow: it shifts required positional arguments, derives `PIP` under the new virtualenv, and performs sequential bootstrap installs. Comments explain `certifi` is installed first to avoid older TLS client issues during setup-requires flows.

State and dependencies: creates the virtualenv directory and installs packages into it; does not itself populate the wheelhouse. Depends on `virtualenv`, network or configured pip access, and a valid Python executable.

Risks: no explicit argument validation beyond shell failures; pip/network issues fail the image prep. It is invoked as `nobody` by `prepare-image.sh`, so permissions are tied to the preceding fix-permissions step.
