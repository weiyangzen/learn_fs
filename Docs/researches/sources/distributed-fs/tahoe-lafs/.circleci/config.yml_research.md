## sources/distributed-fs/tahoe-lafs/.circleci/config.yml

Purpose: primary CircleCI pipeline for Tahoe-LAFS tests, packaging checks, documentation, integration runs, coverage finish, Nix builds, Debian packaging verification, and Docker image builds.

Important elements: pipeline parameters `build-images` and `run-tests`, workflows `ci` and `images`, jobs `debian-12`, Ubuntu variants, `windows-server-2022`, `nixos`, `integration`, `typechecks`, `docs`, `pyinstaller`, `debian-13-package`, `finish-coverage-report`, and `build-image-*`, plus reusable YAML anchors for Docker Hub auth, tox install, setup/test steps, artifacts, and Nix command.

Control flow: normal CI runs platform jobs, code checks, packaging, docs, integration after Debian unit tests, Windows matrix, and coverage finalization. Image builds run only when requested. Debian-style jobs run helper scripts to set up virtualenvs and execute tox as non-root. Windows builds cache pip/wheelhouse, run trial under coverage, upload Coveralls data, and convert subunit results.

State and dependencies: stores test artifacts, caches pip/wheelhouse, uploads coverage to Coveralls, pushes Docker images with Docker Hub context, and fetches Debian packaging sources for Trixie validation.

Risks: embedded Coveralls token and local image tags are sensitive operational dependencies; comments note flaky integration ignore behavior. YAML anchors reduce duplication but make job behavior implicit.
