<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile -->
# sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile

Purpose: minimal container image definition for the Python request-logging web server used in tests.

Important structure: uses `python:3`, adds `server.py` at image root, exposes port 8080, and runs `python ./server.py`.

State, persistence, and integration: creates an image layer containing the server script and exposes a simple HTTP endpoint at runtime. Dependencies include Docker build and the Python base image. Risks include unpinned base image drift, broad `ADD`, and no non-root user. Test signals are container startup and ability to accept/log POST requests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/Dockerfile -->
