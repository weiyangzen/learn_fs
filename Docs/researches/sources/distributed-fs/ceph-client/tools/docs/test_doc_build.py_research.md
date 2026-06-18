<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py -->
# sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py

Purpose: Creates version-specific Sphinx virtual environments and optionally runs kernel documentation builds against them to validate supported Sphinx/version dependency combinations.

Important APIs/types/functions: `DEFAULT_VERSIONS_TO_TEST`, `SPHINX_REQUIREMENTS`, and `PYTHON_VER_CHANGES` encode tested Sphinx/dependency/Python combinations. `AsyncCommands` runs subprocesses asynchronously while teeing output. `SphinxVenv` drives venv creation, pip installs, requirement freezing, optional `make cleandocs` and target builds. `parse_version()` parses CLI versions; `main()` handles version ranges and build options.

Control flow: The script chooses the oldest available Python 3.9-3.12 binary when possible, accumulates incremental package requirements as Sphinx versions increase, then for each requested version creates `Sphinx_<version>`, installs pinned dependencies plus Sphinx, optionally writes `requirements_<version>.txt`, and optionally runs make targets with the venv on `PATH`.

State and persistence: Persistent outputs include `Sphinx_*` virtualenv directories, optional requirements files, optional logs, and build output directories from make. Runtime state tracks elapsed build times.

Dependencies/integration: Depends on `python -m venv`, `pip`, network/package indexes unless cached, `make`, and kernel doc targets. It complements `sphinx-pre-install` by generating/test-driving exact venvs rather than just recommending them.

Risks/tests: Risks include heavy network and build cost, old Sphinx memory behavior, partially created venvs after failure, and dependency pins becoming unavailable. Test signals are dry creation for one version, `--req-file` freeze contents, `--build` on constrained `SPHINXDIRS`, `--min/--max`, `--full`, and log review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/test_doc_build.py -->
